// Card choices in decision mode (P7.E4.S3). Cards such as Headbutt, Armaments or True Grit ask the player to pick
// cards. In the game that opens a selection screen; in a recorded fight the answer comes from the recording. In
// decision mode the host exposes the options and waits for the policy's answer.
//
// Card selections go through the game's own local selector (CardSelectCmd.PushSelector with localOnly = true, the
// mechanism the Whispering Earring relic and the game's AutoSlayer use in ordinary play). The game computes the
// options, the minimum and the maximum itself (enchantable, removable, transformable or upgradable cards ...), asks the
// selector only for the local player's choice, and syncs the answer through PlayerChoiceSynchronizer as in co-op.
// Relic and bundle choices and card rewards have no selector path; they are intercepted at the command or screen.
// The selector is pushed only while Intercept is on, so recorded events replay exactly as recorded.
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

    static bool _intercept;
    static IDisposable _selectorScope;
    public static bool Intercept
    {
        get => _intercept;
        set
        {
            if (value == _intercept) return;
            _intercept = value;
            if (value) _selectorScope = CardSelectCmd.PushSelector(new HostSelector(), true);
            else { _selectorScope?.Dispose(); _selectorScope = null; }
        }
    }
    public static Pending Current;
    // The Crystal Sphere event's minigame: its logic class waits for cell clicks from its screen (inert in the host).
    public static MegaCrit.Sts2.Core.Events.Custom.CrystalSphereEvent.CrystalSphereMinigame Minigame;
    static void MinigamePrefix(MegaCrit.Sts2.Core.Events.Custom.CrystalSphereEvent.CrystalSphereMinigame __instance) { if (_intercept) Minigame = __instance; }
    static bool _installed;
    static string _kind;          // the outermost selection command running, as a label for the observation
    static int _kindDepth;

    // The game hands the local player's card selections to this selector: options, minimum and maximum as the game
    // computed them. The answer arrives later through Answer().
    sealed class HostSelector : MegaCrit.Sts2.Core.TestSupport.ICardSelector
    {
        public Task<IEnumerable<CardModel>> GetSelectedCards(IEnumerable<CardModel> options, int minSelect, int maxSelect)
        {
            var list = options.ToList();
            var max = Math.Min(maxSelect, list.Count);
            var min = Math.Min(minSelect, max);
            var tcs = new TaskCompletionSource<IEnumerable<CardModel>>();
            if (list.Count <= min) tcs.SetResult(list);                                   // forced: every option is taken
            else Current = new Pending { Options = list, Min = min, Max = max, Tcs = tcs, Kind = _kind ?? "Select" };
            return tcs.Task;
        }

        // Card rewards consult only the global selector, which the host never sets.
        public MegaCrit.Sts2.Core.TestSupport.CardRewardSelection GetSelectedCardReward(IReadOnlyList<CardCreationResult> options,
            IReadOnlyList<MegaCrit.Sts2.Core.Entities.CardRewardAlternatives.CardRewardAlternative> alternatives)
            => throw new InvalidOperationException("the host's selector is local-only; card rewards go through the reward screen");
    }

    static void KindPrefix(MethodBase __originalMethod) { if (_kindDepth++ == 0) _kind = __originalMethod.Name; }
    static void KindFinalizer() { _kindDepth = Math.Max(0, _kindDepth - 1); }

    // Must run before the UI classes are made inert (the card reward screen is a UI class).
    public static void Install()
    {
        if (_installed) return;
        _installed = true;
        var kindPrefix = new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(KindPrefix), BindingFlags.Static | BindingFlags.NonPublic));
        var kindFinalizer = new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(KindFinalizer), BindingFlags.Static | BindingFlags.NonPublic));
        foreach (var m in typeof(CardSelectCmd).GetMethods(BindingFlags.Static | BindingFlags.Public).Where(m => m.Name.StartsWith("From") && m.Name != "FromChooseABundleScreen"))
            Stubs.H.Patch(m, prefix: kindPrefix, finalizer: kindFinalizer);
        Stubs.H.Patch(typeof(MegaCrit.Sts2.Core.Events.Custom.CrystalSphereEvent.CrystalSphereMinigame).GetMethod("PlayMinigame")!,
                      prefix: new HarmonyLib.HarmonyMethod(typeof(Choices).GetMethod(nameof(MinigamePrefix), BindingFlags.Static | BindingFlags.NonPublic)));
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
