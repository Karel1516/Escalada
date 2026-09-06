Attribute VB_Name = "modScheduling"
Option Explicit

Public Function FitsTimeBudget(ByVal usedMinutes As Long, ByVal exerciseMinutes As Long, ByVal budgetMinutes As Long) As Boolean
    FitsTimeBudget = (usedMinutes + exerciseMinutes <= budgetMinutes)
End Function
