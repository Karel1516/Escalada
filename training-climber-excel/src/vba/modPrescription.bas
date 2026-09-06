Attribute VB_Name = "modPrescription"
Option Explicit

Public Function IsSafetyBlocked(ByVal exerciseID As String, ByVal state As Object) As Boolean
    Dim excluded As Object: Set excluded = state.Item("exclude")
    IsSafetyBlocked = excluded.Exists("EX:" & exerciseID)
End Function
