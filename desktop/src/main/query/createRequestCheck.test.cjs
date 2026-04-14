const test = require('node:test');
const assert = require('node:assert/strict');

const { detectDeterministicCreateIssues } = require('./createRequestCheck.cjs');

test('detectDeterministicCreateIssues flags unwired event, ref/out mismatch, and method/property misuse', () => {
  const content = `using System;
public partial class FormXDMViewer : Form
{
    private void FormXDMViewer_Load(object sender, EventArgs e)
    {
        LoadAndDisplayXDM("C:\\\\path\\\\to\\\\your\\\\file.xdm");
    }

    private void LoadAndDisplayXDM(string filePath)
    {
        string error = "";
        var loadFile = XRasterIO.LoadFile(filePath, ref error, false);
        var compManager = nxImageLayerComposites1.GetXDMCompManager;
    }
}`;

  const result = detectDeterministicCreateIssues({
    files: [{ path: 'XDMImageViewExample.cs', content }],
    apiFacts: [
      {
        memberName: 'LoadFile',
        kind: 'method',
        stubSignature: 'public XRSLoadFile LoadFile(string filePath, out string error, bool calc, eIOCreateXLDMode mode) { error = string.Empty; return default; }',
      },
      {
        memberName: 'GetXDMCompManager',
        kind: 'method',
        stubSignature: 'public XDMCompManager GetXDMCompManager() { return default; }',
      },
    ],
  });

  assert.ok(result);
  assert.equal(result.needs_changes, true);
  assert.deepEqual(result.target_paths, ['XDMImageViewExample.cs']);
  const joined = result.required_changes.join('\n');
  assert.match(joined, /never wires or invokes it/i);
  assert.match(joined, /calls LoadFile with ref/i);
  assert.match(joined, /uses GetXDMCompManager like a property/i);
});
