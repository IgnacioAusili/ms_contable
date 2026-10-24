Option Explicit

Dim shell, fileSystem, scriptDirectory, powershell, scriptPath, splashPath, action, command, waitForExit

Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

scriptDirectory = fileSystem.GetParentFolderName(WScript.ScriptFullName)
powershell = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")
scriptPath = fileSystem.BuildPath(scriptDirectory, "launch.ps1")
splashPath = fileSystem.BuildPath(scriptDirectory, "launch-splash.ps1")
action = "Start"

If WScript.Arguments.Count > 0 Then
    action = WScript.Arguments(0)
End If

If action <> "Start" And action <> "Stop" Then
    WScript.Quit 2
End If

If action = "Start" Then
    command = """" & powershell & """ -NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & splashPath & """"
Else
    command = """" & powershell & """ -NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & scriptPath & """ -Action Stop"
End If
waitForExit = (action = "Stop")
shell.Run command, 0, waitForExit
