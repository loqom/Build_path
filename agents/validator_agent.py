# 1. Take matched clusters from state
# 2. Send running callback
# 3. For each matched cluster:
#    - Tavily search → "existing tools for {cluster.name}"
#    - Pass results to Groq → "does a solution already exist?"
# 4. Filter out saturated ones
# 5. Send completed callback
# 6. Return { **state, "validated": validated }

