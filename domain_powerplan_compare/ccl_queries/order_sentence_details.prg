select os.order_sentence_id
    , oe_field_display_value = 
        if (osd.default_parent_entity_name = "CODE_VALUE") 
            uar_get_code_display(osd.default_parent_entity_id)
        else osd.oe_field_display_value
        endif
    , order_entry_field = oef.description
from order_sentence os
    , order_sentence_detail osd
    , order_entry_fields oef
    , pathway_comp pc
    , pathway_catalog pwcat
    , pw_comp_os_reltn pcos
plan pwcat where pwcat.active_ind = 1
    and pwcat.end_effective_dt_tm > sysdate
    ; and pwcat.beg_effective_dt_tm < sysdate
    ; and pwcat.type_mean != 'PHASE'
   and pwcat.type_mean = 'PHASE'
join pc where pc.pathway_catalog_id = pwcat.pathway_catalog_id
    and pc.active_ind = 1
    and pc.parent_entity_name = 'ORDER_CATALOG_SYNONYM'
join pcos where pcos.pathway_comp_id = pc.pathway_comp_id
join os where os.order_sentence_id = pcos.order_sentence_id
join osd where osd.order_sentence_id = os.order_sentence_id
join oef where oef.oe_field_id = osd.oe_field_id


/* */
select os.order_sentence_id
    , oe_field_display_value = 
        if (osd.default_parent_entity_name = "CODE_VALUE") 
            uar_get_code_display(osd.default_parent_entity_id)
        else osd.oe_field_display_value
        endif
    , order_entry_field = oef.description
from order_sentence os
    , order_sentence_detail osd
    , order_entry_fields oef
    , pathway_comp pc
    , pathway_catalog pwcat
    , pw_cat_reltn pcr
    , pathway_catalog pwcat2
    , pw_comp_os_reltn pcos
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
    and pc.parent_entity_name = 'ORDER_CATALOG_SYNONYM'
join pcos where pcos.pathway_comp_id = pc.pathway_comp_id
join os where os.order_sentence_id = pcos.order_sentence_id
join osd where osd.order_sentence_id = os.order_sentence_id
join oef where oef.oe_field_id = osd.oe_field_id