def get_tc_notes(startDate,endDate):
    sql = '''
        select
            pj.id pj_id
            ,pj.name pj_name
            ,sat.name sat
            ,convert(varchar(10),tc.pse__end_date__c,121) tc_period
            ,lower(coalesce(pse__Monday_notes__c,'None')) mon_note
            ,pse__Monday_hours__c mon_hrs
            ,lower(coalesce(pse__tuesday_notes__c,'None')) tue_note
            ,pse__tuesday_hours__c tue_hrs
            ,lower(coalesce(pse__wednesday_notes__c,'None')) wed_note
            ,pse__wednesday_hours__c wed_hrs
            ,lower(coalesce(pse__thursday_notes__c,'None')) thu_note
            ,pse__thursday_hours__c thu_hrs
            ,lower(coalesce(pse__friday_notes__c,'None')) fri_note
            ,pse__friday_hours__c fri_hrs
            ,lower(coalesce(pse__timecard_notes__c,'None')) timecard_note
        from  pse__Timecard_Header__c tc
                join pse__proj__c pj on (tc.pse__project__c=pj.id)
                join concur_contact ct on (tc.pse__resource__c=ct.id)
                join service_account_team__c sat on (ct.service_account_team__c=sat.id)
        where 
            --pj.name like 'Admin%'
            pj.name = 'Admin: Other'
            and 
            (pse__Monday_notes__c is not null
            or pse__tuesday_notes__c is not null
            or pse__wednesday_notes__c is not null
            or pse__thursday_notes__c is not null
            or pse__friday_notes__c is not null
            or pse__timecard_notes__c is not null
            )
            and tc.pse__end_date__c between '{0}' and '{1}'
        '''.format(startDate,endDate)
        
    return sql