# Cerner-cross-domain-powerplan-compare
This project uses a combianation of pandas and deepdiff to compare/contrast PowerPlan-specific CCL query output that's run between different Cerner domains of a client site to spot any differences between domains

Differences are split into different categories:
1. PowerPlan only exists in one domain and not the other
2. PowerPlan protocol code has an extra preceding U-, or no longer has an extra preceding U-
3. Actual differences between similarly named PowerPlans
    - Indexed by PowerPlan name, phase name, component sequence and order sentence sequence
    - Components that only exist in one domain's PowerPlan but not the other