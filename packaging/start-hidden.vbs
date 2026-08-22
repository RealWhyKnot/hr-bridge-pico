' Starts the bridge at logon with no console window.
' Put a shortcut to this file in shell:startup. It looks for hr-bridge-pico.exe
' or a .venv beside itself, then one folder up.
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
cmdline = Launcher(here)
If cmdline = "" Then cmdline = Launcher(fso.GetParentFolderName(here))
If cmdline = "" Then
  WScript.Echo "hr-bridge-pico: no hr-bridge-pico.exe and no .venv in " & here & " or its parent."
  WScript.Quit 1
End If
CreateObject("WScript.Shell").Run cmdline, 0, False

Function Launcher(folder)
  Launcher = ""
  If folder = "" Then Exit Function
  exePath = fso.BuildPath(folder, "hr-bridge-pico.exe")
  If fso.FileExists(exePath) Then
    Launcher = """" & exePath & """ --quiet"
    Exit Function
  End If
  pythonw = fso.BuildPath(folder, ".venv\Scripts\pythonw.exe")
  If fso.FileExists(pythonw) Then
    Launcher = """" & pythonw & """ -m hr_bridge_pico --quiet"
  End If
End Function
