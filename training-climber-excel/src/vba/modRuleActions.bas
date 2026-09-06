Attribute VB_Name = "modRuleActions"
Option Explicit

Public Sub ExecuteAction(ByVal actionType As String, ByVal target As String, ByVal actionValue As Variant, ByVal state As Object)
    Select Case UCase$(actionType)
        Case "INCLUDE_EXERCISE": state("include")("EX:" & target) = target
        Case "EXCLUDE_EXERCISE": state("exclude")("EX:" & target) = target
        Case "INCLUDE_CATEGORY": state("include")("CAT:" & target) = target
        Case "EXCLUDE_CATEGORY": state("exclude")("CAT:" & target) = target
        Case "SET_SETS": state("sets") = actionValue
        Case "SET_REPS": state("reps") = actionValue
        Case "SET_DURATION": state("duration") = actionValue
        Case "SET_INTENSITY": state("intensity") = actionValue
        Case "SET_REST": state("rest") = actionValue
        Case "SET_FREQUENCY": state("frequency") = actionValue
        Case "SET_LOAD", "SET_LOAD_PERCENT": state("load") = actionValue
        Case "SET_RPE": state("rpe") = actionValue
        Case "SET_RIR": state("rir") = actionValue
        Case "ALLOW_PROGRESSION": If state("progression") <> "BLOCK" Then state("progression") = "ALLOW"
        Case "BLOCK_PROGRESSION": state("progression") = "BLOCK"
        Case "TRIGGER_DELOAD": state("progression") = "DELOAD"
        Case "TRIGGER_REEVALUATION": state("progression") = "REEVALUATE"
        Case "SHOW_WARNING": state("warnings") = state("warnings") & IIf(Len(state("warnings")) > 0, vbCrLf, "") & CStr(actionValue)
        Case "SET_MIN", "SET_MAX", "MULTIPLY_VOLUME": state(LCase$(actionType)) = actionValue
        Case Else: Err.Raise vbObjectError + 130, "ExecuteAction", "Acción desconocida: " & actionType
    End Select
End Sub
