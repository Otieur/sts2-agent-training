"""Combat models (P9.E2): tensors from encodings (`tools/learn/encode.py`) and the value network.

Runs with the project's PyTorch environment: `.venv-learn/bin/python -I` (security review:
`docs/reviews/learning-framework-security-review.md`). Checkpoints are the project's own and are loaded with
`weights_only=True` only.

The value network reads one encoded observation and predicts the fight's result under the policy that generated the
data: the chance to win, the HP left if it wins, and the enemies' HP left if it loses. `expected_value` turns the three
into the same scale as the search's value (`tools/sim.py _value`: HP left after a win, -100 minus the enemies' HP
left after a loss), so the network can stand in for a rollout at a search leaf.
"""
import torch
import torch.nn as nn

import encode as E

SETS = {  # field: (kind of index, cap)
    "hand_ids": ("cards", E.MAX_HAND), "draw_ids": ("cards", E.MAX_PILE), "discard_ids": ("cards", E.MAX_PILE),
    "exhaust_ids": ("cards", E.MAX_PILE), "choice_ids": ("cards", E.MAX_CHOICE), "ppow_ids": ("powers", E.MAX_POWERS),
    "enemy_ids": ("monsters", E.MAX_ENEMIES), "epow_ids": ("powers", E.MAX_ENEMIES * E.MAX_POWERS),
    "relic_ids": ("relics", E.MAX_RELICS), "potion_ids": ("potions", E.MAX_POTIONS),
}
FLOAT_SETS = {  # field: (width, cap)
    "hand_feats": (len(E.HAND_FEATS), E.MAX_HAND), "enemy_feats": (len(E.ENEMY_FEATS), E.MAX_ENEMIES),
    "ppow_amt": (2, E.MAX_POWERS), "epow_amt": (2, E.MAX_ENEMIES * E.MAX_POWERS), "mates": (len(E.MATE_FEATS), E.MAX_MATES),
}
UPG = {"draw_upg": E.MAX_PILE, "discard_upg": E.MAX_PILE, "exhaust_upg": E.MAX_PILE, "choice_upg": E.MAX_CHOICE}


def collate(encs):
    """Encodings to a dict of padded tensors (index 0 = padding, so masks are `ids > 0`)."""
    b = len(encs)
    out = {"glob": torch.tensor([e["glob"] for e in encs], dtype=torch.float32)}
    for f, (_, cap) in SETS.items():
        t = torch.zeros(b, cap, dtype=torch.long)
        for i, e in enumerate(encs):
            v = e[f][:cap]
            if v:
                t[i, :len(v)] = torch.tensor(v)
        out[f] = t
    for f, (w, cap) in FLOAT_SETS.items():
        t = torch.zeros(b, cap, w)
        for i, e in enumerate(encs):
            v = e[f][:cap]
            if v:
                t[i, :len(v)] = torch.tensor(v)
        out[f] = t
    for f, cap in UPG.items():
        t = torch.zeros(b, cap)
        for i, e in enumerate(encs):
            v = e[f][:cap]
            if v:
                t[i, :len(v)] = torch.tensor(v)
        out[f] = t
    t = torch.zeros(b, E.MAX_ENEMIES * E.MAX_POWERS, dtype=torch.long)
    for i, e in enumerate(encs):
        v = e["epow_owner"][:t.shape[1]]
        if v:
            t[i, :len(v)] = torch.tensor(v)
    out["epow_owner"] = t
    out["mates_mask"] = (out["mates"].abs().sum(-1) > 0).float()
    return out


def index_batch(batch, idx):
    return {k: v[idx] for k, v in batch.items()}


def to_device(batch, device):
    return {k: v.to(device) for k, v in batch.items()}


def _mlp(i, h, o, drop=0.0):
    return nn.Sequential(nn.Linear(i, h), nn.ReLU(), nn.Dropout(drop), nn.Linear(h, o), nn.ReLU())


def _pool(x, mask):
    """Masked sum and max over a set: x [B, L, D], mask [B, L] -> [B, 2D]."""
    m = mask.unsqueeze(-1)
    s = (x * m).sum(1)
    mx = torch.where(m > 0, x, torch.full_like(x, -1e4)).max(1).values
    mx = torch.where(mask.sum(1, keepdim=True) > 0, mx, torch.zeros_like(mx))
    return torch.cat([s, mx], -1)


def _mean(x, mask):
    m = mask.unsqueeze(-1)
    return (x * m).sum(1) / m.sum(1).clamp(min=1)


class ValueNet(nn.Module):
    def __init__(self, sizes, card_dim=32, hidden=256, drop=0.1, set_drop=0.0):
        """Outputs [win logit, HP left if won / 100, enemy HP left if lost / 100]; the last two are residuals on the
        current HP and the current enemy HP, so the network learns the change from now to the end of the fight.
        `set_drop`: during training, each relic, potion and pile card is hidden with this probability, so the network
        cannot recognize a source run by its exact relic set and deck (it memorized them otherwise)."""
        super().__init__()
        self.config = {"sizes": sizes, "card_dim": card_dim, "hidden": hidden, "drop": drop, "set_drop": set_drop, "encoder": E.ENCODER_VERSION}
        self.set_drop = set_drop
        d = card_dim
        self.card = nn.Embedding(sizes["cards"], d, padding_idx=0)
        self.upg = nn.Parameter(torch.zeros(d))
        self.power = nn.Embedding(sizes["powers"], 16, padding_idx=0)
        self.monster = nn.Embedding(sizes["monsters"], d, padding_idx=0)
        self.relic = nn.Embedding(sizes["relics"], 16, padding_idx=0)
        self.potion = nn.Embedding(sizes["potions"], 8, padding_idx=0)
        self.hand = _mlp(d + len(E.HAND_FEATS), 96, 64, drop)
        self.ppow = _mlp(16 + 2, 32, 32)
        self.epow = _mlp(16 + 2, 32, 32)
        self.enemy = _mlp(d + len(E.ENEMY_FEATS) + 32, 96, 64, drop)
        self.mate = _mlp(len(E.MATE_FEATS), 16, 16)
        width = len(E.GLOBAL_FIELDS) + 128 + 4 * d + 32 + 128 + 32 + 8 + 32   # glob, hand, 3 piles + choice, powers, enemies, relics, potions, mates
        self.trunk = nn.Sequential(nn.Linear(width, hidden), nn.ReLU(), nn.Dropout(drop), nn.Linear(hidden, 128), nn.ReLU())
        self.head = nn.Linear(128, 3)   # win logit, HP left if won (/100), enemy HP left if lost (/100)
        names = [f[0] for f in E.GLOBAL_FIELDS]
        self._hp, self._ehp = names.index("hp"), names.index("enemy_hp_total")
        self._ehp_scale = E.GLOBAL_FIELDS[self._ehp][2] / 100.0

    def cards(self, ids, upg=None):
        x = self.card(ids)
        if upg is not None:
            x = x + upg.unsqueeze(-1) * self.upg
        return x

    def _hide(self, ids):
        if self.training and self.set_drop > 0:
            return ids * (torch.rand(ids.shape, device=ids.device) >= self.set_drop).long()
        return ids

    def features(self, b):
        """Shared state encoding: the trunk input, per-card hand vectors [B, H, 64] and per-enemy vectors [B, E, 64]."""
        if self.training and self.set_drop > 0:
            b = dict(b)
            for f in ("relic_ids", "potion_ids", "draw_ids", "discard_ids", "exhaust_ids"):
                b[f] = self._hide(b[f])
        hm = (b["hand_ids"] > 0).float()
        hand = self.hand(torch.cat([self.cards(b["hand_ids"], b["hand_feats"][..., 0]), b["hand_feats"]], -1))
        piles = [_mean(self.cards(b[p + "_ids"], b[p + "_upg"]), (b[p + "_ids"] > 0).float()) for p in ("draw", "discard", "exhaust")]
        choice = _mean(self.cards(b["choice_ids"], b["choice_upg"]), (b["choice_ids"] > 0).float())
        pm = (b["ppow_ids"] > 0).float()
        ppow = _pool(self.ppow(torch.cat([self.power(b["ppow_ids"]), b["ppow_amt"]], -1)), pm)[:, :32]
        em = (b["enemy_ids"] > 0).float()
        epm = (b["epow_ids"] > 0).float()
        ep = self.epow(torch.cat([self.power(b["epow_ids"]), b["epow_amt"]], -1)) * epm.unsqueeze(-1)       # [B, P, 32]
        owner = torch.nn.functional.one_hot(b["epow_owner"], E.MAX_ENEMIES).float() * epm.unsqueeze(-1)  # [B, P, E]
        per_enemy = owner.transpose(1, 2) @ ep                                                         # [B, E, 32]
        enemy = self.enemy(torch.cat([self.monster(b["enemy_ids"]), b["enemy_feats"], per_enemy], -1))
        rm = (b["relic_ids"] > 0).float()
        relics = _pool(self.relic(b["relic_ids"]), rm)[:, :16]
        relics = torch.cat([relics, _mean(self.relic(b["relic_ids"]), rm)], -1)
        potions = (self.potion(b["potion_ids"]) * (b["potion_ids"] > 0).float().unsqueeze(-1)).sum(1)
        mates = _pool(self.mate(b["mates"]), b["mates_mask"])
        x = torch.cat([b["glob"], _pool(hand, hm), *piles, choice, ppow, _pool(enemy, em), relics, potions, mates], -1)
        return x, hand, enemy

    def forward(self, b):
        x, _, _ = self.features(b)
        h = self.head(self.trunk(x))
        # Residual outputs: HP left = current HP + predicted change; enemy HP left = current enemy HP + predicted change.
        g = b["glob"]
        return torch.stack([h[:, 0], g[:, self._hp] + h[:, 1], g[:, self._ehp] * self._ehp_scale + h[:, 2]], -1)


def expected_value(out):
    """Network outputs to the search's value scale: p * HP_if_won + (1 - p) * (-100 - enemy_HP_if_lost)."""
    p = torch.sigmoid(out[..., 0])
    hp = out[..., 1].clamp(min=0) * 100
    left = out[..., 2].clamp(min=0) * 100
    return p * hp + (1 - p) * (-100 - left)


MAX_CANDS = 6


def collate_actions(cands_list):
    """Candidate actions (play a hand card at an optional target, or end the turn) to tensors; choices are not scored."""
    b = len(cands_list)
    kind = torch.zeros(b, MAX_CANDS, dtype=torch.long)       # 0 none, 1 play, 2 end turn
    card = torch.zeros(b, MAX_CANDS, dtype=torch.long)
    target = torch.zeros(b, MAX_CANDS, dtype=torch.long)
    has_target = torch.zeros(b, MAX_CANDS)
    for i, cands in enumerate(cands_list):
        for j, a in enumerate(cands[:MAX_CANDS]):
            if a["type"] == "play":
                kind[i, j] = 1
                card[i, j] = min(a.get("card", 0), E.MAX_HAND - 1)
                if a.get("target") is not None:
                    target[i, j] = min(a["target"], E.MAX_ENEMIES - 1)
                    has_target[i, j] = 1
            elif a["type"] == "end_turn":
                kind[i, j] = 2
    return {"act_kind": kind, "act_card": card, "act_target": target, "act_has_target": has_target}


class QNet(ValueNet):
    """Action values (P9.E3.S1): the value network's state encoding plus, for each candidate, the vector of the card it
    plays and of its target; predicts the search's value of that candidate (/100). Scoring candidates needs no host
    call at all, so it is the fastest policy (and a prior for search)."""
    def __init__(self, sizes, card_dim=32, hidden=256, drop=0.1, set_drop=0.0):
        super().__init__(sizes, card_dim, hidden, drop, set_drop)
        self.config["kind"] = "q"
        self.kind_emb = nn.Embedding(3, 16)
        self.q = nn.Sequential(nn.Linear(128 + 16 + 64 + 64 + 1, 128), nn.ReLU(), nn.Dropout(drop), nn.Linear(128, 1))

    def forward(self, b):
        x, hand, enemy = self.features(b)
        s = self.trunk(x)                                                      # [B, 128]
        c = b["act_kind"].shape[1]
        gather = lambda t, idx: torch.gather(t, 1, idx.unsqueeze(-1).expand(-1, -1, t.shape[-1]))
        card_v = gather(hand, b["act_card"]) * (b["act_kind"] == 1).float().unsqueeze(-1)
        tgt_v = gather(enemy, b["act_target"]) * b["act_has_target"].unsqueeze(-1)
        z = torch.cat([s.unsqueeze(1).expand(-1, c, -1), self.kind_emb(b["act_kind"]), card_v, tgt_v, b["act_has_target"].unsqueeze(-1)], -1)
        return self.q(z).squeeze(-1)                                           # [B, C], search value / 100


def save(model, path, extra=None):
    torch.save({"config": model.config, "state": model.state_dict(), "extra": extra or {}}, path)


def load(path, device="cpu"):
    ck = torch.load(path, map_location=device, weights_only=True)
    cfg = ck["config"]
    m = (QNet if cfg.get("kind") == "q" else ValueNet)(cfg["sizes"], cfg["card_dim"], cfg["hidden"], cfg["drop"], cfg.get("set_drop", 0.0))
    m.load_state_dict(ck["state"])
    m.eval()
    return m, ck.get("extra", {})
