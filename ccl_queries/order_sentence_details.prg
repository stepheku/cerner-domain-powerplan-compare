/*
order_sentence_details.prg
~~~~~~~~~~~~~~~~~~~~
Grabs all discrete order sentence details based on the pathway_catalog table
Save to data/os_detail_b0783.csv or data/os_detail_p0783.csv
*/
select domain = curdomain
    , os.order_sentence_id
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
    , pw_comp_os_reltn pcos
    , pathway_catalog pwcat
    , pathway_catalog pwcat2
    , pw_cat_reltn pcr
plan pwcat where pwcat.active_ind = 1
    and pwcat.type_mean in ("CAREPLAN", "PATHWAY")
    ; and pwcat.description_key like "ONCP*"
    and pwcat.version = (
        select max(pwcat4.version)
        from pathway_catalog pwcat4
        where pwcat4.version_pw_cat_id = pwcat.version_pw_cat_id
            and pwcat4.active_ind = 1
    )
    and pwcat.end_effective_dt_tm > cnvtdatetime(curdate,curtime3)
    ; and pwcat.pathway_type_cd in (
    ;     value(uar_get_code_by("DISPLAY_KEY", 30183, "ONCOLOGY"))
    ;     , value(uar_get_code_by("DISPLAY_KEY", 30183, "COMPASSIONATEACCESSPROGRAM"))
    ;     , value(uar_get_code_by("DISPLAY_KEY", 30183, "ONCOLOGYMULTIDISCIPLINARY"))
    ; )
join pcr where pcr.pw_cat_s_id = outerjoin(pwcat.pathway_catalog_id)
    and pcr.type_mean = outerjoin("GROUP")
join pwcat2 where pwcat2.pathway_catalog_id = outerjoin(pcr.pw_cat_t_id)
join pc where pc.active_ind = 1
    and pc.pathway_catalog_id in (
        pwcat.pathway_catalog_id
        , pwcat2.pathway_catalog_id
    )
join pcos where pcos.pathway_comp_id = pc.pathway_comp_id
join os where os.order_sentence_id = pcos.order_sentence_id
join osd where osd.order_sentence_id = os.order_sentence_id
join oef where oef.oe_field_id = osd.oe_field_id
