select powerplan_description = pwcat.description
    , phase = pwcat2.description
    , phase_duration = concat(trim(cnvtstring(pwcat2.duration_qty)), 
                                   " ", 
                                   uar_get_code_display(pwcat2.duration_unit_cd))
    , component_type =
        if(pwcat.type_mean = "PATHWAY") uar_get_code_display(pc.comp_type_cd)
        else uar_get_code_display(pc2.comp_type_cd)
        endif
    , start_offset = concat(trim(cnvtstring(pc.offset_quantity)), 
                                 " ", 
                                 uar_get_code_display(pc.offset_unit_cd))
    , target_duration = concat(trim(cnvtstring(pc.duration_qty)),
                                    " ", 
                                    uar_get_code_display(pc.duration_unit_cd))
    , include = evaluate2(
        if(pwcat.type_mean = "PATHWAY") pc.include_ind
        elseif(pwcat.type_mean = "CAREPLAN") pc2.include_ind
        endif)
    , sequence = evaluate2(
        if(pwcat.type_mean = "PATHWAY") pc.sequence
        elseif(pwcat.type_mean = "CAREPLAN") pc2.sequence
        endif)
    , synonym = evaluate2(
        if(pwcat.type_mean = "PATHWAY")
            if(pc.parent_entity_name = "ORDER_CATALOG_SYNONYM") ocs.mnemonic
            elseif(pc.parent_entity_name = "LONG_TEXT") TRIM(substring(0,512,lt.long_text))
            elseif(pc.parent_entity_name = "OUTCOME_CATALOG") oc.description 
            endif
        elseif(pwcat.type_mean = "CAREPLAN")
            if(pc2.parent_entity_name = "ORDER_CATALOG_SYNONYM") ocs3.mnemonic
            elseif(pc2.parent_entity_name = "LONG_TEXT") TRIM(substring(0,512,lt3.long_text)) 
            endif
        endif)
from pathway_catalog pwcat
    , pathway_catalog pwcat2
    , pw_cat_reltn pcr
    , pathway_comp pc
    , pathway_comp pc2
    , order_catalog_synonym ocs
    , order_catalog_synonym ocs3
    , long_text lt
    , long_text lt3
    , outcome_catalog oc
    , pw_cat_flex pcf
plan pwcat where pwcat.active_ind = 1
    and pwcat.type_mean in ("CAREPLAN", "PATHWAY")
    and pwcat.description_key like 'ONC*'
    and pwcat.description_key not like 'ONCOLOGY*'
    and pwcat.end_effective_dt_tm > cnvtdatetime(curdate,curtime3)
    and pwcat.beg_effective_dt_tm < cnvtdatetime(curdate,curtime3)
    and pwcat.ref_owner_person_id = 0
join pcr where pcr.pw_cat_s_id = outerjoin(pwcat.pathway_catalog_id)
join pwcat2 where pwcat2.pathway_catalog_id = outerjoin(pcr.pw_cat_t_id)
    and pwcat2.sub_phase_ind = outerjoin(0)
    and pwcat2.active_ind = outerjoin(1)
join pc where pc.pathway_catalog_id = outerjoin(pwcat2.pathway_catalog_id)
    and pc.active_ind = outerjoin(1)
join pc2 where pc2.pathway_catalog_id = outerjoin(pwcat.pathway_catalog_id)
    and pc2.active_ind = outerjoin(1)
join ocs where ocs.synonym_id = outerjoin(pc.parent_entity_id)
join oc where oc.outcome_catalog_id = outerjoin(pc.parent_entity_id)
join lt where lt.long_text_id = outerjoin(pc.parent_entity_id)
join ocs3 where ocs3.synonym_id = outerjoin(pc2.parent_entity_id)
join lt3 where lt3.long_text_id = outerjoin(pc2.parent_entity_id)
join pcf where pcf.pathway_catalog_id = pwcat.pathway_catalog_id
    and pcf.parent_entity_id = (
        select c.code_value
        from code_value c
        where c.code_set = 220
            and c.active_ind = 1
            and c.cdf_meaning = 'FACILITY'
            and c.display_key like 'SPH*ST*PAUL*'
        )
order by pwcat.description_key
    , pwcat2.pathway_catalog_id
    , phase
    , pc.sequence