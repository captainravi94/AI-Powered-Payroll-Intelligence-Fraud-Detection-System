def decision_logic(fraud, risk):
    if fraud == 1 and risk > 1:
        return "🚨 Audit Immediately"
    elif risk > 0.8:
        return "⚠️ Review Payroll"
    else:
        return "✅ Approved"