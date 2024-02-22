/*
pathway_query.prg
~~~~~~~~~~~~~~~~~~~~
Grabs as much pathway information as possible. Note that each level of a PowerPlan
is a pathway. This includes:
- PowerPlan
- Phase
- DOTs
Saved to data/b0783_pathway.csv or data/p0783_pathway.csv
*/

select
    pathway_catalog_id = pwcat.pathway_catalog_id
    , description = pwcat.description
    , display_description = pwcat.display_description
    , plan_type = uar_get_code_display(pwcat.pathway_type_cd)
    , cross_encounter_ind = pwcat.cross_encntr_ind
    , evidence_link = if(findstring("URL:", per.evidence_locator) > 0)
            substring(5, 512, per.evidence_locator)
        else
            per.evidence_locator
        endif
    , check_alerts_on_plan_updt_ind = pwcat.alerts_on_plan_upd_ind
    , check_alerts_on_planning_ind = pwcat.alerts_on_plan_ind
    , allow_diagnosis_propagation_ind = pwcat.diagnosis_capture_ind
    , hide_flexed_components = pwcat.hide_flexed_comp_ind
    , cycle_use_numbers_ind = pwcat.cycle_ind
    , cycle_std_nbr = pwcat.standard_cycle_nbr
    , beg_cycle_nbr = pwcat.cycle_begin_nbr
    , end_cycle_nbr = pwcat.cycle_end_nbr
    , cycle_incrm_nbr = pwcat.cycle_increment_nbr
    , disp_std_nbr_or_end_val_ind = pwcat.cycle_display_end_ind
    , restr_ability_to_mod_std_nbr_ind = pwcat.cycle_lock_end_ind
    , cycle_disp_val = uar_get_code_display(pwcat.cycle_label_cd)
    , default_view_mean = pwcat.default_view_mean
    , prompt_for_ordering_physician_ind = pwcat.provider_prompt_ind
    , copy_forward_ind = pwcat.allow_copy_forward_ind
    , display_method = uar_get_code_display(pwcat.display_method_cd)
    , classification = uar_get_code_display(pwcat.pathway_class_cd)
    , do_not_allow_proposal_ind = pwcat.restricted_actions_bitmask
    , route_for_review = 
        if(pwcat.route_for_review_ind = 1)
            if(pwcat.review_required_sig_count in (0, 1)) "Route for 1 review"
            elseif(pwcat.review_required_sig_count = 2) "Route for 2 reviews"
            else "None"
            endif
        else
            "None"
        endif
    , plan_ord_def_default_visit =
        if (pwcat.default_visit_type_flag = 0) "None"
        elseif (pwcat.default_visit_type_flag = 1) "This Visit"
        elseif (pwcat.default_visit_type_flag = 2) "Future Inpatient"
        elseif (pwcat.default_visit_type_flag = 3) "Future Outpatient"
        endif
    , phase_pathway_catalog_id = pwcat2.pathway_catalog_id
    , phase_description = pwcat2.description
    , phase_primary_phase_ind = pwcat2.primary_ind
    , phase_optional_phase_ind = pwcat2.optional_ind
    , phase_future_phase_ind = pwcat2.future_ind
    , phase_open_by_default = pwcat2.open_by_default_ind
    , phase_this_visit_outpt =
        uar_get_code_display(pwcat2.default_action_outpt_now_cd)
    , phase_this_visit_inpt =
        uar_get_code_display(pwcat2.default_action_inpt_now_cd)
    , phase_future_visit_outpt =
        uar_get_code_display(pwcat2.default_action_outpt_future_cd)
    , phase_future_visit_inpt =
        uar_get_code_display(pwcat2.default_action_inpt_future_cd)
    , phase_check_alerts_on_planning_ind =
        pwcat2.alerts_on_plan_ind
    , phase_check_alerts_on_plan_updt_ind =
        pwcat2.alerts_on_plan_upd_ind
    , phase_route_for_review = 
        if(pwcat2.route_for_review_ind = 1)
            if(pwcat2.review_required_sig_count in (0, 1)) "Route for 1 review"
            elseif(pwcat2.review_required_sig_count = 2) "Route for 2 reviews"
            else "None"
            endif
        else
            "None"
        endif
    , phase_duration_qty =
        pwcat2.duration_qty
    , phase_duration_unit =
        uar_get_code_display(pwcat2.duration_unit_cd)
    , phase_pathway_class =
        uar_get_code_display(pwcat2.pathway_class_cd)
    , phase_document_resch_reason =
        if (pwcat2.reschedule_reason_accept_flag = 0) "Off"
        elseif (pwcat2.reschedule_reason_accept_flag = 1) "Optional"
        elseif (pwcat2.reschedule_reason_accept_flag = 2) "Required"
        endif
    , dot_pathway_catalog_id = pwcat3.pathway_catalog_id
    , dot_description = pwcat3.description
    , dot_duration_qty = pwcat3.duration_qty
    , dot_duration_unit = uar_get_code_display(pwcat3.duration_unit_cd)
from pathway_catalog pwcat
    , pw_evidence_reltn per
    , pw_cat_reltn pcr
    , pathway_catalog pwcat2
    , pw_cat_reltn pcr2
    , pathway_catalog pwcat3
plan pwcat where pwcat.active_ind = 1
    and pwcat.type_mean in ("CAREPLAN", "PATHWAY")
    and pwcat.end_effective_dt_tm > sysdate
    and pwcat.version = (
        select max(pwcat4.version)
        from pathway_catalog pwcat4
        where pwcat4.version_pw_cat_id = pwcat.version_pw_cat_id
            and pwcat4.active_ind = 1
    )
    and pwcat.ref_owner_person_id = 0
join per where per.pathway_catalog_id = outerjoin(pwcat.pathway_catalog_id)
    and per.type_mean != outerjoin("EVENTSET")
join pcr where pcr.pw_cat_s_id = outerjoin(pwcat.pathway_catalog_id)
    and pcr.type_mean = outerjoin("GROUP")
join pwcat2 where pwcat2.pathway_catalog_id = outerjoin(pcr.pw_cat_t_id)
join pcr2 where pcr2.pw_cat_s_id = outerjoin(pwcat2.pathway_catalog_id)
    and pcr2.type_mean = outerjoin("GROUP")
join pwcat3 where pwcat3.pathway_catalog_id = outerjoin(pcr2.pw_cat_t_id)