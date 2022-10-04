/*
pathway_components.prg
~~~~~~~~~~~~~~~~~~~~
Grabs PowerPlan components based on the parameters specified on the pathway_catalog
table
This is saved to: ONCP_comp_b0783.csv or ONCP_comp_p0783.csv
*/
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
    , oc2.orderable_type_flag
    , iv_component = ocs2.mnemonic
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
    , linking_rule = pcg.description
    , pcg.linking_rule_quantity
    , linking_rule_flag =
       if(pcg.linking_rule_flag = 0) ""
       elseif(pcg.linking_rule_flag = 1) "At Least"
       elseif(pcg.linking_rule_flag = 2) "Exactly"
       elseif(pcg.linking_rule_flag = 3) "At Most"
       endif
   , linking_override_reason =
       if(pcg.override_reason_flag = 0 and pcg.pathway_comp_id > 0) "Tooltip only"
       elseif(pcg.override_reason_flag = 1) "Required"
       endif
    , assigned_dots = comp_dot.dot
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
    , order_catalog_synonym ocs2
    , pathway_catalog pwcat3
    , order_catalog oc2
    , ( ( 
        select distinct pc.pathway_comp_id
            , dot = listagg(pwcat4.description , ", ")
                over(partition by pc.pathway_comp_id order by pwcat4.period_nbr asc)
        from pathway_comp pc
            , pw_comp_cat_reltn pccr
            , pathway_catalog pwcat4
        where pc.active_ind = 1
            and pc.parent_entity_name = "ORDER_CATALOG_SYNONYM"
            and pccr.pathway_comp_id = pc.pathway_comp_id
            and pwcat4.pathway_catalog_id = pccr.pathway_catalog_id
            and pwcat4.type_mean = "DOT"
        with sqltype("f8", "vc")) comp_dot )
    , pw_comp_group pcg

plan pwcat where pwcat.active_ind = 1
    and pwcat.type_mean in ("CAREPLAN", "PATHWAY")
    and pwcat.description_key like "ONCP*"
    and pwcat.version = (
        select max(pwcat4.version)
        from pathway_catalog pwcat4
        where pwcat4.version_pw_cat_id = pwcat.version_pw_cat_id
            and pwcat4.active_ind = 1
    )
    and pwcat.end_effective_dt_tm > cnvtdatetime(curdate,curtime3)
    and pwcat.pathway_type_cd in (
        value(uar_get_code_by("DISPLAY_KEY", 30183, "ONCOLOGY"))
        , value(uar_get_code_by("DISPLAY_KEY", 30183, "COMPASSIONATEACCESSPROGRAM"))
        , value(uar_get_code_by("DISPLAY_KEY", 30183, "ONCOLOGYMULTIDISCIPLINARY"))
    )
join pcr where pcr.pw_cat_s_id = outerjoin(pwcat.pathway_catalog_id)
    and pcr.type_mean = outerjoin("GROUP")
join pwcat2 where pwcat2.pathway_catalog_id = outerjoin(pcr.pw_cat_t_id)
join pc where pc.active_ind = 1
    and pc.pathway_catalog_id in (
        pwcat.pathway_catalog_id
        , pwcat2.pathway_catalog_id
    )
join comp_dot where comp_dot.pathway_comp_id = outerjoin(pc.pathway_comp_id)
join pcg where pcg.pathway_comp_id = outerjoin(pc.pathway_comp_id)
join lt2 where lt2.long_text_id = outerjoin(pc.parent_entity_id)
    and lt2.active_ind = outerjoin(1)
join oc where oc.outcome_catalog_id = outerjoin(pc.parent_entity_id)
    and oc.active_ind = outerjoin(1)
join pwcat3 where pwcat3.pathway_catalog_id = outerjoin(pc.parent_entity_id)
    and pwcat3.active_ind = outerjoin(1)
join pcos where pcos.pathway_comp_id = outerjoin(pc.pathway_comp_id)
join ocs2 where ocs2.synonym_id = outerjoin(pcos.iv_comp_syn_id)
join os where os.order_sentence_id = outerjoin(pcos.order_sentence_id)
join ocs where ocs.synonym_id = outerjoin(pc.parent_entity_id)
join oc2 where oc2.catalog_cd = outerjoin(ocs.catalog_cd)
join lt where lt.long_text_id = outerjoin(os.ord_comment_long_text_id)
    and lt.active_ind = outerjoin(1)
order by pwcat.description_key
    , pwcat2.pathway_catalog_id
    , phase
    , pc.sequence
    , pcos.order_sentence_seq
    , ocs2.mnemonic_key_cap