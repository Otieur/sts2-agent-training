// Card choices in decision mode (P7.E4.S3). Cards such as Headbutt, Armaments or True Grit ask the player to pick
// cards. In the game that opens a selection screen; in a recorded fight the answer comes from the recording. In
// decision mode the host intercepts the selection commands, exposes the options, and waits for the policy's answer.
// The interception is off while recorded events are applied, so the past is replayed exactly as recorded.
using System.Reflection;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;

public static class Choices
{
    public sealed class Pending
    {
        public List<CardModel> Options = new();
        public int Min, Max;
        public bool Single;
        public object Tcs;
        public string Kind = "";
        public List<string> Extra = new();            // card reward alternatives after the cards (skip, reroll ...)
        public List<RelicModel> Relics;               // relic choice
        public List<List<CardModel>> Bundles;         // bundle choice

        public int Count => Relics?.Count ?? Bundles?.Count ?? Options.Count + Extra.Count;
        public IEnumerable<string> Labels() => Relics != null ? Relics.Select(r => r.Id.Entry)
            : Bundles != null ? Bundles.Select(b => string.Join("+", b.Select(c => c.Id.Entry)))
            : Options.Select(c => c.Id.Entry + (c.IsUpgraded ? "+" : "")).Concat(Extra.Select(e => "alt:" + e));
    }

    public static bool Intercept;
    public static Pending Current;
    static bool _installed;

    // Must run before the UI classes are made inert (the card reward screen is a UI class).
    public static void Install()
    {
        if (_installed) return;
        _installed = true;
        var prefix = new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(Prefix), BindingFlags.Static | BindingFlags.NonPublic));
        foreach (var name in new[] { "FromCombatPile", "FromHand", "FromHandForDiscard", "FromHandForUpgrade", "FromSimpleGrid", "FromChooseACardScreen",
                                     "FromSimpleGridForRewards", "FromDeckForUpgrade", "FromDeckForRemoval", "FromDeckGeneric",
                                     "FromDeckForTransformation", "FromDeckForEnchantment" })
            foreach (var m in typeof(CardSelectCmd).GetMethods(BindingFlags.Static | BindingFlags.Public).Where(m => m.Name == name))
                Stubs.H.Patch(m, prefix: prefix);
        var relic = typeof(RelicSelectCmd).GetMethod("FromChooseARelicScreen", BindingFlags.Static | BindingFlags.Public)!;
        Stubs.H.Patch(relic, prefix: new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(RelicPrefix), BindingFlags.Static | BindingFlags.NonPublic)));
        var bundle = typeof(CardSelectCmd).GetMethod("FromChooseABundleScreen", BindingFlags.Static | BindingFlags.Public)!;
        Stubs.H.Patch(bundle, prefix: new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(BundlePrefix), BindingFlags.Static | BindingFlags.NonPublic)));
        // Card rewards: the game shows a selection screen and awaits its OptionSelected(): an index into the offered cards
        // followed by the alternatives (skip, reroll ...), or null to close the screen without a pick.
        var screen = typeof(MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NCardRewardSelectionScreen);
        var show = screen.GetMethod("ShowScreen", BindingFlags.Static | BindingFlags.Public)!;
        var picked = screen.GetMethod("OptionSelected", BindingFlags.Instance | BindingFlags.Public)!;
        Stubs.Reserve(show); Stubs.Reserve(picked);
        Stubs.H.Patch(show, prefix: new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(RewardShowPrefix), BindingFlags.Static | BindingFlags.NonPublic)));
        Stubs.H.Patch(picked, prefix: new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(RewardPickPrefix), BindingFlags.Static | BindingFlags.NonPublic)));
    }

    static List<string> _rewardOptions = new();
    static List<CardModel> _rewardCards = new();

    static bool RewardShowPrefix(IReadOnlyList<CardCreationResult> options, IReadOnlyList<MegaCrit.Sts2.Core.Entities.CardRewardAlternatives.CardRewardAlternative> extraOptions, ref object __result)
    {
        _rewardCards = options.Select(o => o.Card).ToList();
        _rewardOptions = extraOptions.Select(a => a.OptionId).ToList();
        __result = Stubs.InertInstance(typeof(MegaCrit.Sts2.Core.Nodes.Screens.CardSelection.NCardRewardSelectionScreen));
        return false;
    }

    static bool RewardPickPrefix(ref Task<int?> __result)
    {
        var tcs = new TaskCompletionSource<int?>();
        __result = tcs.Task;
        Current = new Pending { Options = _rewardCards, Min = 0, Max = 1, Single = true, Tcs = tcs, Kind = "CardReward", Extra = _rewardOptions };
        return false;
    }

    static bool RelicPrefix(Player player, IReadOnlyList<RelicModel> relics, ref Task<RelicModel> __result)
    {
        if (!Intercept) return true;
        var tcs = new TaskCompletionSource<RelicModel>();
        __result = tcs.Task;
        if (relics.Count <= 1) tcs.SetResult(relics.FirstOrDefault());
        else Current = new Pending { Relics = relics.ToList(), Min = 1, Max = 1, Single = true, Tcs = tcs, Kind = "ChooseARelic" };
        return false;
    }

    static bool BundlePrefix(Player player, IReadOnlyList<IReadOnlyList<CardModel>> bundles, ref Task<IEnumerable<CardModel>> __result)
    {
        if (!Intercept) return true;
        var tcs = new TaskCompletionSource<IEnumerable<CardModel>>();
        __result = tcs.Task;
        if (bundles.Count <= 1) tcs.SetResult(bundles.FirstOrDefault() ?? (IReadOnlyList<CardModel>)Array.Empty<CardModel>());
        else Current = new Pending { Bundles = bundles.Select(b => b.ToList()).ToList(), Min = 1, Max = 1, Single = true, Tcs = tcs, Kind = "ChooseABundle" };
        return false;
    }

    static bool Prefix(MethodBase __originalMethod, object[] __args, ref object __result)
    {
        if (!Intercept) return true;
        var m = (MethodInfo)__originalMethod;
        var player = __args.OfType<Player>().FirstOrDefault();
        var fromDeck = m.Name.StartsWith("FromDeck");
        var cards = __args.OfType<CardPile>().FirstOrDefault()?.Cards
                    ?? __args.OfType<IReadOnlyList<CardModel>>().FirstOrDefault()
                    ?? __args.OfType<List<CardCreationResult>>().FirstOrDefault()?.Select(r => r.Card)
                    ?? (fromDeck ? player!.Deck.Cards : (IEnumerable<CardModel>)player!.PlayerCombatState.Hand.Cards);
        var filter = __args.OfType<Func<CardModel, bool>>().FirstOrDefault();
        var options = cards.Where(c => filter == null || filter(c)).ToList();
        if (m.Name is "FromHandForUpgrade" or "FromDeckForUpgrade") options = options.Where(c => c.IsUpgradable).ToList();
        var single = m.ReturnType == typeof(Task<CardModel>);
        int min = 1, max = 1;
        if (__args.FirstOrDefault(a => a is CardSelectorPrefs) is CardSelectorPrefs prefs) { min = prefs.MinSelect; max = prefs.MaxSelect; }
        if (m.Name == "FromChooseACardScreen" && __args.OfType<bool>().FirstOrDefault()) min = 0;
        max = Math.Min(max, options.Count);
        min = Math.Min(min, max);
        if (single)
        {
            var tcs = new TaskCompletionSource<CardModel>();
            __result = tcs.Task;
            if (options.Count == 0) tcs.SetResult(null);
            else if (options.Count == 1 && min >= 1) tcs.SetResult(options[0]);       // a forced pick needs no decision
            else Current = new Pending { Options = options, Min = min, Max = 1, Single = true, Tcs = tcs, Kind = m.Name };
        }
        else
        {
            var tcs = new TaskCompletionSource<IEnumerable<CardModel>>();
            __result = tcs.Task;
            if (options.Count <= min) tcs.SetResult(options);                          // forced: every option is taken
            else Current = new Pending { Options = options, Min = min, Max = max, Tcs = tcs, Kind = m.Name };
        }
        return false;
    }

    public static void Answer(IReadOnlyList<int> picks)
    {
        var p = Current ?? throw new InvalidOperationException("no choice is pending");
        if (picks.Count < p.Min || picks.Count > p.Max || picks.Distinct().Count() != picks.Count || picks.Any(i => i < 0 || i >= p.Count))
            throw new ArgumentException($"choose between {p.Min} and {p.Max} of {p.Count} options");
        Current = null;
        if (p.Kind == "CardReward") { ((TaskCompletionSource<int?>)p.Tcs).SetResult(picks.Count == 0 ? null : picks[0]); return; }
        if (p.Relics != null) { ((TaskCompletionSource<RelicModel>)p.Tcs).SetResult(p.Relics[picks[0]]); return; }
        if (p.Bundles != null) { ((TaskCompletionSource<IEnumerable<CardModel>>)p.Tcs).SetResult(p.Bundles[picks[0]]); return; }
        var chosen = picks.Select(i => p.Options[i]).ToList();
        if (p.Single) ((TaskCompletionSource<CardModel>)p.Tcs).SetResult(chosen.FirstOrDefault());
        else ((TaskCompletionSource<IEnumerable<CardModel>>)p.Tcs).SetResult(chosen);
    }
}
