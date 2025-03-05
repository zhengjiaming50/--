Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 检查是否在脚本所在目录运行
If Not fso.FileExists("一键安装所有环境.bat") Then
    MsgBox "请将本文件与所有脚本放在同一目录后运行！", vbCritical, "路径错误"
    WScript.Quit
End If

Do While True
    userChoice = MsgBox("林地报告生成系统" & vbCrLf & vbCrLf & _
                        "请选择操作：" & vbCrLf & vbCrLf & _
                        "1. 安装运行环境" & vbCrLf & _
                        "2. 处理PDF文件" & vbCrLf & _
                        "3. 处理Excel文件" & vbCrLf & _
                        "4. 合成文本文件" & vbCrLf & _
                        "5. 一键全自动运行", _
                        vbQuestion + vbYesNoCancel + vbDefaultButton1, _
                        "主操作菜单")
    
    Select Case userChoice
        Case vbYes
            objShell.Run "cmd /c 一键安装所有环境.bat", 1, True
        Case vbNo
            userChoice = MsgBox("请选择要执行的操作：" & vbCrLf & vbCrLf & _
                                "1. PDF转文本" & vbCrLf & _
                                "2. Excel数据处理", _
                                vbQuestion + vbRetryCancel + vbDefaultButton1, _
                                "二级菜单")
            
            If userChoice = vbRetry Then
                objShell.Run "cmd /c 处理pdf.bat", 1, True
            Else
                objShell.Run "cmd /c 处理excel.bat", 1, True
            End If
        Case vbCancel
            If MsgBox("是否要退出系统？", vbQuestion + vbYesNo, "退出确认") = vbYes Then
                Exit Do
            End If
        Case Else
            Exit Do
    End Select
Loop

MsgBox "感谢使用林地报告生成系统！", vbInformation, "退出系统" 