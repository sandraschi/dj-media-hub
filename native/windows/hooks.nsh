; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillDjMediaHubFleetProcesses
  DetailPrint "Stopping dj-media-hub processes..."
  ExecWait 'taskkill /F /IM dj-media-hub-backend.exe /T' $0
  ExecWait 'taskkill /F /IM dj-media-hub-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "dj-media-hub-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "dj-media-hub-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "dj-media-hub-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "dj-media-hub-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillDjMediaHubFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillDjMediaHubFleetProcesses
!macroend

!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register dj-media-hub in Cursor / Claude Desktop"
    ExecWait 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\resources\install-mcp-clients.ps1" -Interactive'
  mcp_hook_done:
!macroend