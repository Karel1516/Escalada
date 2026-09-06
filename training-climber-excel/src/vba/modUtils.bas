Attribute VB_Name = "modUtils"
Option Explicit

Public Function FindTable(ByVal tableName As String) As ListObject
    Dim ws As Worksheet, lo As ListObject
    For Each ws In ThisWorkbook.Worksheets
        For Each lo In ws.ListObjects
            If StrComp(lo.Name, tableName, vbTextCompare) = 0 Then Set FindTable = lo: Exit Function
        Next lo
    Next ws
End Function

Public Function ColIndex(ByVal lo As ListObject, ByVal columnName As String) As Long
    On Error GoTo Missing
    ColIndex = lo.ListColumns(columnName).Index
    Exit Function
Missing:
    Err.Raise vbObjectError + 101, "ColIndex", "Columna inexistente: " & lo.Name & "." & columnName
End Function

Public Function CellValue(ByVal lo As ListObject, ByVal rowIndex As Long, ByVal columnName As String) As Variant
    CellValue = lo.DataBodyRange.Cells(rowIndex, ColIndex(lo, columnName)).Value2
End Function

Public Function NewID(ByVal prefix As String) As String
    Randomize
    NewID = prefix & "-" & Format$(Now, "yyyymmddhhnnss") & "-" & Format$(Int(Rnd * 10000), "0000")
End Function

Public Function JsonSafe(ByVal value As Variant) As String
    JsonSafe = Replace(Replace(CStr(value), "\", "\\"), Chr$(34), "\" & Chr$(34))
End Function

Public Function NamedValue(ByVal nameText As String, Optional ByVal fallback As Variant = "") As Variant
    On Error GoTo Missing
    NamedValue = ThisWorkbook.Names(nameText).RefersToRange.Value2
    Exit Function
Missing:
    NamedValue = fallback
End Function

Public Function IsTruthy(ByVal value As Variant) As Boolean
    If VarType(value) = vbBoolean Then IsTruthy = CBool(value): Exit Function
    Dim text As String: text = UCase$(Trim$(CStr(value)))
    IsTruthy = (text = "TRUE" Or text = "VERDADERO" Or text = "1" Or text = "YES" Or text = "SI" Or text = "SÍ")
End Function
