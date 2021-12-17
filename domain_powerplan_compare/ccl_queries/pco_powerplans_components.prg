select powerplan_description = pwcat.description
    , phase = pwcat2.description
    , plan_display_method = uar_get_code_display(pwcat.display_method_cd)
    , phase_display_method = uar_get_code_display(pwcat2.display_method_cd)
    , pc.sequence
    , dcp_clin_cat = uar_get_code_display(pc.dcp_clin_cat_cd)
    , dcp_clin_sub_cat = uar_get_code_display(pc.dcp_clin_sub_cat_cd)
    , bgcolor_red = if(findstring('<BackColor>', pc.display_format_xml) > 0)
        cnvtb16b10(
            substring(
            findstring('<BackColor>', pc.display_format_xml) + textlen('<BackColor>') + 6, 2,
            pc.display_format_xml),
            2 ) endif
    , bgcolor_green = if(findstring('<BackColor>', pc.display_format_xml) > 0)
        cnvtb16b10(
            substring(
            findstring('<BackColor>', pc.display_format_xml) + textlen('<BackColor>') + 4, 2,
            pc.display_format_xml),
            2 ) endif
    , bgcolor_blue = if(findstring('<BackColor>', pc.display_format_xml) > 0)
        cnvtb16b10(
            substring(
            findstring('<BackColor>', pc.display_format_xml) + textlen('<BackColor>') + 2, 2,
            pc.display_format_xml),
            2 ) endif
    , component = if(pc.parent_entity_name = 'ORDER_CATALOG_SYNONYM')ocs.mnemonic
        elseif(pc.parent_entity_name = 'OUTCOME_CATALOG') oc.description
        elseif(pc.parent_entity_name = 'LONG_TEXT') substring(0, 1000, lt2.long_text)
        elseif(pc.parent_entity_name = 'PATHWAY_CATALOG') substring(0, 1000, pwcat3.description)
        endif
    , target_duration = if(pc.duration_qty = 0) ""
        else concat(trim(cnvtstring(pc.duration_qty)), " ", 
            uar_get_code_display(pc.duration_unit_cd))
        endif
    , start_offset = if(pc.offset_quantity = 0) ""
        else concat(trim(cnvtstring(pc.offset_quantity)), " ", 
            uar_get_code_display(pc.offset_unit_cd))
        endif
    , link_duration_to_phase = pc.linked_to_tf_ind
    , pc.required_ind
    , pc.include_ind
    , pc.chemo_ind
    , pc.chemo_related_ind
    , pc.persistent_ind
    , pcos.order_sentence_seq
    , os.order_sentence_id
    , order_comment = trim(lt.long_text)
from pathway_catalog pwcat
    , pathway_catalog pwcat2
    , pw_cat_reltn pcr
    , pathway_comp pc
    , order_catalog_synonym ocs
    , pw_comp_os_reltn pcos
    , order_sentence os
    , long_text lt
    , long_text lt2
    , outcome_catalog oc
    , pathway_catalog pwcat3
plan pwcat where pwcat.active_ind = 1
    and pwcat.type_mean in ("PATHWAY")
    and pwcat.description_key not like 'Z*'
    and pwcat.description_key like 'ONCP*'
;    and pwcat.description_key not like 'ONCOLOGY*'
    and pwcat.version = (
        select max(pwcat4.version)
        from pathway_catalog pwcat4
        where pwcat4.version_pw_cat_id = pwcat.version_pw_cat_id
            and pwcat4.active_ind = 1
        )
    and pwcat.end_effective_dt_tm > cnvtdatetime(curdate,curtime3)
    ; and pwcat.beg_effective_dt_tm < cnvtdatetime(curdate,curtime3)
    and pwcat.ref_owner_person_id = 0
join pcr where pcr.pw_cat_s_id = pwcat.pathway_catalog_id
join pwcat2 where pwcat2.pathway_catalog_id = pcr.pw_cat_t_id
    and pwcat2.sub_phase_ind = 0
    and pwcat2.active_ind = 1
join pc where pc.pathway_catalog_id = pwcat2.pathway_catalog_id
    and pc.active_ind = 1
join lt2 where lt2.long_text_id = outerjoin(pc.parent_entity_id)
    and lt2.active_ind = outerjoin(1)
join oc where oc.outcome_catalog_id = outerjoin(pc.parent_entity_id)
    and oc.active_ind = outerjoin(1)
join pwcat3 where pwcat3.pathway_catalog_id = outerjoin(pc.parent_entity_id)
    and pwcat3.active_ind = outerjoin(1)
join pcos where pcos.pathway_comp_id = outerjoin(pc.pathway_comp_id)
join os where os.order_sentence_id = outerjoin(pcos.order_sentence_id)
join ocs where ocs.synonym_id = outerjoin(pc.parent_entity_id)
join lt where lt.long_text_id = outerjoin(os.ord_comment_long_text_id)
    and lt.active_ind = outerjoin(1)
order by pwcat.description_key
    , pwcat2.pathway_catalog_id
    , phase
    , pc.sequence
