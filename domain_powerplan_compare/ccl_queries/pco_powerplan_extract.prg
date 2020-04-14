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
    , iv_builder_component = ocs2.mnemonic
    , pcos.order_sentence_seq
    , order_sentence = evaluate2(
        if(pwcat.type_mean = "PATHWAY")
            if(pc.parent_entity_name = "OUTCOME_CATALOG") oc.expectation
            else os.order_sentence_display_line
            endif
        elseif(pwcat.type_mean = "CAREPLAN") os2.order_sentence_display_line
        endif)
    , order_comments = evaluate2(
        if(pwcat.type_mean = "PATHWAY") trim(substring(0,512,lt2.long_text))
        elseif(pwcat.type_mean = "CAREPLAN") trim(substring(0,512,lt4.long_text))
        endif)
from pathway_catalog pwcat
    , pathway_catalog pwcat2
    , pw_cat_reltn pcr
    , pathway_comp pc
    , pathway_comp pc2
    , order_catalog_synonym ocs
    , order_catalog_synonym ocs3
    , pw_comp_os_reltn pcos
    , pw_comp_os_reltn pcos2
    , order_sentence os
    , order_sentence os2
    , long_text lt
    , long_text lt2
    , long_text lt3
    , long_text lt4
    , order_catalog_synonym ocs2
    , outcome_catalog oc
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

/*Order sentence stuff*/
join pcos where pcos.pathway_comp_id = outerjoin(pc.pathway_comp_id)
join os where os.order_sentence_id = outerjoin(pcos.order_sentence_id)
join lt2 where lt2.long_text_id = outerjoin(os.ord_comment_long_text_id)
join ocs2 where ocs2.synonym_id = outerjoin(pcos.iv_comp_syn_id)

/*Order sentence stuff for non-phased powerplans*/
join pcos2 where pcos2.pathway_comp_id = outerjoin(pc2.pathway_comp_id)
join os2 where os2.order_sentence_id = outerjoin(pcos2.order_sentence_id)
join lt4 where lt4.long_text_id = outerjoin(os2.ord_comment_long_text_id)

order by pwcat.description_key
    , pwcat2.pathway_catalog_id
    , phase
    , pc.sequence
    , pcos.order_sentence_seq