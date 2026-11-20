// Reads the game's assembly (sts2.dll) metadata and IL with the .NET runtime only: no decompiler, no third-party code.
// Used to check how the game engine works before building against it (simulation spike, after game updates).
//
//   dotnet run tools/asm/asm.cs -- index <dll> <out.txt>          types, fields, properties, methods
//   dotnet run tools/asm/asm.cs -- calls <dll> <out.tsv>          per method: called methods, touched fields, string literals
//   dotnet run tools/asm/asm.cs -- il <dll> <name substring>      IL listing of the matching methods (stdout)
//
// Outputs stay out of git (data/asm/ is ignored): they describe the game's code and change with every patch.
#:property PublishAot=false
using System.Reflection;
using System.Reflection.Emit;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;

if (args.Length < 3) { Console.Error.WriteLine("usage: index|calls <dll> <out> | il <dll> <pattern>"); return 2; }
var mode = args[0];
using var fs = File.OpenRead(args[1]);
using var pe = new PEReader(fs);
var md = pe.GetMetadataReader();
var ops = new Dictionary<short, OpCode>();
foreach (var f in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static)) { var o = (OpCode)f.GetValue(null)!; ops[o.Value] = o; }

string TName(EntityHandle h)
{
    switch (h.Kind)
    {
        case HandleKind.TypeDefinition:
        {
            var t = md.GetTypeDefinition((TypeDefinitionHandle)h);
            var n = md.GetString(t.Name);
            var d = t.GetDeclaringType();
            if (!d.IsNil) return TName(d) + "+" + n;
            var ns = md.GetString(t.Namespace);
            return ns.Length > 0 ? ns + "." + n : n;
        }
        case HandleKind.TypeReference:
        {
            var t = md.GetTypeReference((TypeReferenceHandle)h);
            var n = md.GetString(t.Name);
            if (t.ResolutionScope.Kind == HandleKind.TypeReference) return TName((EntityHandle)t.ResolutionScope) + "+" + n;
            var ns = md.GetString(t.Namespace);
            return ns.Length > 0 ? ns + "." + n : n;
        }
        case HandleKind.TypeSpecification:
        {
            var br = md.GetBlobReader(md.GetTypeSpecification((TypeSpecificationHandle)h).Signature);
            if (br.ReadSignatureTypeCode() == SignatureTypeCode.GenericTypeInstance) { br.ReadSignatureTypeCode(); return TName(br.ReadTypeHandle()) + "<>"; }
            return "(spec)";
        }
    }
    return "?";
}

string MName(EntityHandle h) => h.Kind switch
{
    HandleKind.MethodDefinition => TName(md.GetMethodDefinition((MethodDefinitionHandle)h).GetDeclaringType()) + "::" + md.GetString(md.GetMethodDefinition((MethodDefinitionHandle)h).Name),
    HandleKind.MemberReference => TName(md.GetMemberReference((MemberReferenceHandle)h).Parent) + "::" + md.GetString(md.GetMemberReference((MemberReferenceHandle)h).Name),
    HandleKind.MethodSpecification => MName(md.GetMethodSpecification((MethodSpecificationHandle)h).Method),
    HandleKind.FieldDefinition => TName(md.GetFieldDefinition((FieldDefinitionHandle)h).GetDeclaringType()) + "::" + md.GetString(md.GetFieldDefinition((FieldDefinitionHandle)h).Name),
    _ => "?",
};

// Decodes one method body; returns (offset, text) per instruction.
List<(int, string)> Decode(MethodDefinition m)
{
    var res = new List<(int, string)>();
    var il = pe.GetMethodBody(m.RelativeVirtualAddress).GetILReader();
    while (il.RemainingBytes > 0)
    {
        var off = il.Offset;
        short v = il.ReadByte();
        if (v == 0xFE) v = (short)(0xFE00 | il.ReadByte());
        var op = ops[v];
        string arg = "";
        switch (op.OperandType)
        {
            case OperandType.InlineNone: break;
            case OperandType.ShortInlineBrTarget: { var d = (sbyte)il.ReadByte(); arg = $"-> {il.Offset + d:X4}"; break; }
            case OperandType.InlineBrTarget: { var d = il.ReadInt32(); arg = $"-> {il.Offset + d:X4}"; break; }
            case OperandType.ShortInlineI: case OperandType.ShortInlineVar: arg = il.ReadByte().ToString(); break;
            case OperandType.InlineVar: arg = il.ReadInt16().ToString(); break;
            case OperandType.InlineI: arg = il.ReadInt32().ToString(); break;
            case OperandType.InlineI8: arg = il.ReadInt64().ToString(); break;
            case OperandType.InlineR: arg = il.ReadDouble().ToString(); break;
            case OperandType.ShortInlineR: arg = il.ReadSingle().ToString(); break;
            case OperandType.InlineSwitch: { var n = il.ReadInt32(); for (var i = 0; i < n; i++) il.ReadInt32(); arg = $"({n} targets)"; break; }
            case OperandType.InlineMethod:
            {
                var h = MetadataTokens.EntityHandle(il.ReadInt32());
                arg = (op.Value == OpCodes.Newobj.Value ? "new:" : "") + MName(h); break;
            }
            case OperandType.InlineField: arg = "f:" + MName(MetadataTokens.EntityHandle(il.ReadInt32())); break;
            case OperandType.InlineString:
            {
                var s = md.GetUserString(MetadataTokens.UserStringHandle(il.ReadInt32() & 0xFFFFFF));
                arg = "str:" + (s.Length > 60 ? s[..60] : s).Replace("\n", " ").Replace("|", "/"); break;
            }
            default: { var tok = il.ReadInt32(); arg = (tok >> 24) is 0x01 or 0x02 or 0x1B ? TName(MetadataTokens.EntityHandle(tok)) : ""; break; }
        }
        res.Add((off, $"{op.Name} {arg}".TrimEnd()));
    }
    return res;
}

if (mode == "index")
{
    using var w = new StreamWriter(args[2]);
    foreach (var h in md.TypeDefinitions)
    {
        var t = md.GetTypeDefinition(h);
        var tn = TName(h);
        var bt = t.BaseType.IsNil ? "" : TName(t.BaseType);
        w.WriteLine($"T {tn} : {bt} [{t.Attributes}]");
        foreach (var fh in t.GetFields())
        {
            var f = md.GetFieldDefinition(fh);
            var val = "";
            var ch = f.GetDefaultValue();
            if (!ch.IsNil)
            {
                var c = md.GetConstant(ch);
                var br = md.GetBlobReader(c.Value);
                val = " = " + (c.TypeCode switch
                {
                    ConstantTypeCode.Int32 => br.ReadInt32().ToString(), ConstantTypeCode.Int64 => br.ReadInt64().ToString(),
                    ConstantTypeCode.Int16 => br.ReadInt16().ToString(), ConstantTypeCode.Byte => br.ReadByte().ToString(),
                    ConstantTypeCode.Boolean => br.ReadBoolean().ToString(), ConstantTypeCode.Single => br.ReadSingle().ToString(),
                    ConstantTypeCode.Double => br.ReadDouble().ToString(), ConstantTypeCode.String => "\"" + br.ReadUTF16(br.Length) + "\"",
                    _ => c.TypeCode.ToString(),
                });
            }
            w.WriteLine($"  F {tn}::{md.GetString(f.Name)}{val} [{f.Attributes}]");
        }
        foreach (var ph in t.GetProperties()) w.WriteLine($"  P {tn}::{md.GetString(md.GetPropertyDefinition(ph).Name)}");
        foreach (var mh in t.GetMethods()) { var m = md.GetMethodDefinition(mh); w.WriteLine($"  M {tn}::{md.GetString(m.Name)} [{m.Attributes}] params={m.GetParameters().Count}"); }
    }
    return 0;
}
if (mode == "calls")
{
    using var w = new StreamWriter(args[2]);
    foreach (var th in md.TypeDefinitions)
        foreach (var mh in md.GetTypeDefinition(th).GetMethods())
        {
            var m = md.GetMethodDefinition(mh);
            if (m.RelativeVirtualAddress == 0) continue;
            var refs = Decode(m).Select(x => x.Item2).Where(s => s.Contains("::") || s.Contains("str:"))
                .Select(s => s[(s.IndexOf(' ') + 1)..]);
            w.WriteLine(MName(mh) + "\t" + string.Join("|", refs));
        }
    return 0;
}
if (mode == "il")
{
    foreach (var th in md.TypeDefinitions)
        foreach (var mh in md.GetTypeDefinition(th).GetMethods())
        {
            var m = md.GetMethodDefinition(mh);
            if (m.RelativeVirtualAddress == 0 || !MName(mh).Contains(args[2])) continue;
            Console.WriteLine("### " + MName(mh));
            foreach (var (off, s) in Decode(m)) Console.WriteLine($"  {off:X4} {s}");
        }
    return 0;
}
Console.Error.WriteLine("unknown mode " + mode);
return 2;
