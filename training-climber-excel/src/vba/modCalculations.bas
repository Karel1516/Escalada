Attribute VB_Name = "modCalculations"
Option Explicit

Public Function RelativeStrength(ByVal forceKg As Double, ByVal bodyMassKg As Double) As Variant
    If bodyMassKg <= 0 Then RelativeStrength = CVErr(xlErrDiv0) Else RelativeStrength = forceKg / bodyMassKg
End Function

Public Function SessionLoad(ByVal minutes As Double, ByVal rpe As Double) As Double
    SessionLoad = minutes * rpe
End Function
