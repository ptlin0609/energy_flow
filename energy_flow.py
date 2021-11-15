#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 12:39:17 2021

@author: mlin
"""

import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import plotly.express as px
import plotly
import plotly.graph_objects as go
import streamlit.components as stc
import base64

#password security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password,hashed_text):
    if make_hashes(password)==hashed_text:
        return hashed_text
    return False

#Login Database
import sqlite3
conn=sqlite3.connect('login.db')
c=conn.cursor()
def create_usertable():
    c.execute("CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)")
    
def add_userdata(username,password):
    c.execute("INSERT INTO userstable(username,password) VALUES (?,?)",(username,password))
    conn.commit()
    
def login_user(username,password):
    c.execute("SELECT * FROM userstable WHERE username=? AND password=?", (username,password))
    data=c.fetchall()
    return data

def view_all_users():
    c.execute("SELECT * FROM userstable")
    data=c.fetchall()
    return data
#variables
capacity={'Jabel Ali':8695,'Al Aweer':1996,'Hassyan':600,'MBR Solar':1013,'Shams Dubai':164}
co2_factor={'natural_gas':0.053, 'coal':0.095}

#energy calc
def annual_generation(capacity,cf,fuel):
    '''cf needs to be decimal point'''
    if fuel=='Water':
        return capacity*cf*365
    elif fuel=='Electricity':
        return capacity*cf/100*8.76
    else:
        return 'This fuel type is not supported'
    
def water_cf(reported_consumption,capacity_sum):
    return reported_consumption/(capacity_sum*365)

def efficiency(facility,cf,annual_generation,thermal_efficiency=1,water_generation=1,desal_heat=1,annual_insolation=1,land=1):
    if facility=='Jabel Ali':
        desal_heat_output=water_generation*4546*desal_heat/1000000
        primary_en_consumption=(annual_generation+desal_heat_output)/(thermal_efficiency/100)
        ans=annual_generation/primary_en_consumption
    elif facility=='MBR Solar':
        ans=annual_generation/(land*annual_insolation)
    return ans

def csv_downloader(data,new_filename):
    csvfile=data.to_csv()
    b64=base64.b64encode(csvfile.encode()).decode()
    href=f'<a href="data:file/csv;base64,{b64}" download={new_filename}>Download csv file</a>'
    st.markdown(href,unsafe_allow_html=True)
    

heat_convert=0.27276
e_convert=0.013638
btu_convert=3412
w_convert=220

#main code
def main():
    st.title("DEWA Energy Flow Analytics")
    menu=["Home","Login", "Sign up"]
    action=st.sidebar.selectbox("Menu", menu)
    if action=="Home":
        st.write("### Please ***Login/Sign Up*** from the sidebar")
    elif action=="Login":
        username=st.sidebar.text_input("Username")
        password=st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            hashed_pswd=make_hashes(password)
            
            result=login_user(username,check_hashes(password,hashed_pswd))
            if result:
                st.success("Logged in as {}".format(username))
                task=st.selectbox("Function",["DEWA", "General Test Case"])
                variable=['country','occupancy_type','cooling_type','metering_infrastructure', 
                              'year_built']
                
                    
                if task=="General Test Case":
                    with st.form(key='consumption records'):
                        statistics=st.file_uploader('DEWA Annual Statistics',type=['csv','txt','xlsx'])
                        if statistics:
                            statisticdf=pd.read_csv(statistics, thousands=',')
                            st.dataframe(statisticdf)
                            rescon=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Residential')]['value'].values
                            comcon=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Commercial')]['value'].values
                            indcon=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Industrial')]['value'].values
                            auxcon=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Auxilary')]['value'].values
                            othcon=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Others')]['value'].values
                            allcon=statisticdf.loc[statisticdf.item_name=='Energy Requirement']['value'].values
                            wrescon=statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Residential')]['value'].values
                            wcomcon=statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Commercial')]['value'].values
                            windcon=statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Industrial')]['value'].values
                            wothcon=statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Others')]['value'].values
                            wallcon=statisticdf.loc[statisticdf.item_name=='Total System Requirement (Desalinated Water)']['value'].values
                        
                            st.subheader('Electricity Consumption (GWh)')
                            col1,col2,col3=st.beta_columns([3,2,1])
                            with col1:
                                e_res=st.number_input("Residential", float(rescon)) 
                                e_comm=st.number_input("Commercial", float(comcon))
                                e_aux=st.number_input("Power & Water Auxillary", float(auxcon))
                            with col2:
                                e_ind=st.number_input("Industrial", float(indcon))
                                e_other=st.number_input("Other", float(othcon))
                            st.write("Annual Reported Consumption")
                            reported_e=st.number_input("Reported Electricity Consumption (GWh)", float(allcon))
                            
                            st.subheader('Water Consumption (MIG)')
                            col1,col2,col3=st.beta_columns([3,2,1])
                            with col1:
                                w_res=st.number_input("Residential Water", float(wrescon))
                                w_comm=st.number_input("Commercial Water", float(wcomcon))
                            with col2:
                                w_ind=st.number_input("Industrial Water", float(windcon))
                                w_other=st.number_input("Other Water", float(wothcon))
                            st.write("Annual Reported Consumption")
                            reported_w=st.number_input("Reported Water Consumption (MIG)",float(wallcon))
                            
                            submit_button4=st.form_submit_button(label='Save')
                            if submit_button4:
                                st.write("Your consumption records have been saved")
                        else:
                            col1,col2,col3=st.beta_columns([3,2,1])
                            with col1:
                                e_res=st.number_input("Residential") 
                                e_comm=st.number_input("Commercial")
                                e_aux=st.number_input("Power & Water Auxillary")
                            with col2:
                                e_ind=st.number_input("Industrial")
                                e_other=st.number_input("Other")
                            st.write("Annual Reported Consumption")
                            reported_e=st.number_input("Reported Electricity Consumption (GWh)")
                            
                            st.subheader('Water Consumption (MIG)')
                            col1,col2,col3=st.beta_columns([3,2,1])
                            with col1:
                                w_res=st.number_input("Residential Water")
                                w_comm=st.number_input("Commercial Water")
                            with col2:
                                w_ind=st.number_input("Industrial Water")
                                w_other=st.number_input("Other Water")
                            st.write("Annual Reported Consumption")
                            reported_w=st.number_input("Reported Water Consumption (MIG)")
                            
                            submit_button4=st.form_submit_button(label='Save')
                            if submit_button4:
                                st.write("Your consumption records have been saved")
                    with st.form(key='form1'):
                        st.subheader('CCGT')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf1=st.number_input("Capacity Factor % (CCGT)",float(0),float(500000000000),float(50),0.1)
                            capacity1=st.number_input("CCGT Capacity (MW)",float(0),float(500000000000),float(8695),0.1)  
                        with col2:
                            thermal_efficiency1=st.number_input("Thermal Efficiency % (CCGT)",float(0),float(500000000000),float(82),0.1)
                        
                        st.subheader('Desalination Plant')
                        st.write("Desalination Plant MSF")
                        thermal_e=st.number_input("Thermal to Electric Factor",0.6)
                        desal_heat1=st.number_input("Desalination Heat Demand (kWh/m3)",60)
                        heat_convert=desal_heat1/220
                        desal_elec_msf_1=st.number_input("MSF Desalination Electricity Demand (kWh/m3)",3)/220
                        st.write("Desalination Plant RO")
                        desal_elec_ro_1=st.number_input("RO Desalination Electricity Demand (kWh/m3)",3)/220
                            
                        
                        st.subheader('SCGT')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf21=st.number_input("Capacity Factor % (SCGT)",float(0),float(500000000000),10.0,0.1)
                            capacity21=st.number_input("SCGT Capacity (MW)",float(0),float(500000000000),1996.0,0.1)  
                        with col2:
                            efficiency21=st.number_input("Efficiency % (SCGT)",float(0),float(500000000000),33.0,0.1)
                            
                        
                        st.subheader('Coal')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf3=st.number_input("Capacity Factor % (USC Coal)",float(0),float(500000000000),17.5,0.1)
                            capacity3=st.number_input("USC Coal Capacity (MW)",float(0),float(500000000000),2400.0,0.1)
                        with col2:
                            efficiency3=st.number_input("Efficiency % (USC Coal)",float(0),float(500000000000),40.0,0.1)
                        
                            
                        st.subheader('Ground-mount Solar')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf4=st.number_input("Capacity Factor % (Ground-mount PV)",float(0),float(500000000000),30.0,0.1)
                            capacity4=st.number_input("Ground-mount PV Capacity (MW)",float(0),float(500000000000),1013.0,0.1)
                            epbt=st.number_input("Energy Payback Time",0) 
                            epbt=epbt if epbt!=0 else  1
                        with col2:
                            annual_insolation4=st.number_input("Annual Insolation (kWh/m2)",float(0),float(500000000000),2100.0,0.1)
                            land_area4=st.number_input("Land Area (km2)",float(0),float(500000000000),15.0,0.1)
                            
                        st.subheader('Distribued Rooftop Solar')
                        capacity5=capacity['Shams Dubai']
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf5=st.number_input("Capacity Factor % (Distribued Rooftop PV)",float(0),float(500000000000),25.0,0.1)
                            capacity5=st.number_input("Distribued Rooftop PV Capacity (MW)",float(0),float(500000000000),164.0,0.1)
                        with col2:
                            efficiency5=st.number_input("Efficiency %(Distribued Rooftop PV)",float(0),float(500000000000),15.0,0.1)
                            
                        st.subheader('Nuclear')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            nuclear_con=st.number_input("Nuclear Import (GWh)")
                        
                        submit_button=st.form_submit_button(label="Submit")
                        if submit_button:
                            st.write("Your input has been submitted. Results are calculated below")
                            with st.beta_expander("Results"):
                                ag1=annual_generation(capacity1, cf1, 'Electricity')
                                ag2=annual_generation(capacity21, cf21, 'Electricity')
                                ag3=annual_generation(capacity3, cf3, 'Electricity')
                                ag4=annual_generation(capacity4, cf4, 'Electricity')
                                ag5=annual_generation(capacity5, cf5, 'Electricity')
                                desal_cf=water_cf(reported_w,470)
                                #msf_water_generation=annual_generation(445, desal_cf, 'Water')
                                msf_heat_con=thermal_e*ag1
                                msf_water_generation=msf_heat_con/heat_convert
                                #msf_e_con=msf_water_generation*e_convert
                                #msf_e_con=msf_water_generation/desal_elec_msf_1
                                ro_water_generation=annual_generation(25, desal_cf, 'Water')
                                #ro_e_con=ro_water_generation*e_convert
                                ro_e_con=ro_water_generation*desal_elec_ro_1
                                
                                h_boiler=(reported_w-ro_water_generation)*heat_convert-msf_heat_con
                                w_sup=msf_water_generation+ro_water_generation+h_boiler/heat_convert-reported_w
                                msf_e_con=(desal_elec_msf_1/desal_heat1)*(msf_heat_con+h_boiler)
                                
                                total_we_con=ro_e_con+msf_heat_con+msf_e_con+h_boiler
                                efficiency1=efficiency('Jabel Ali',cf1,ag1,thermal_efficiency1,msf_water_generation,desal_heat1)
                                efficiency4=efficiency('MBR Solar',cf4,ag4,thermal_efficiency1,msf_water_generation,desal_heat1,annual_insolation4,land=land_area4)
                                #pe1=(ag1+msf_heat_con)/efficiency1 if efficiency1!=0 else 0
                                pe1=(ag1+msf_heat_con)/(thermal_efficiency1/100) if thermal_efficiency1!=0 else 0
                                pe2=ag2/(efficiency21/100) if efficiency21!=0 else 0
                                pe3=ag3/(efficiency3/100) if efficiency3!=0 else 0
                                pe4=ag4/efficiency4 if efficiency4!=0 else 0
                                pe5=ag5/(efficiency5/100) if efficiency5!=0 else 0
                                
                                #co2 calculation 
                                gas_co2=(pe1+pe2)*btu_convert*co2_factor['natural_gas']
                                coal_co2=pe3*btu_convert*co2_factor['coal']
                                solar_co2=((epbt)/25)*0.09*btu_convert*(ag4+ag5)
                                
                                #Surplus
                                surplus=ag1+ag2+ag3+ag4+ag5-reported_e
                                st.write("Electricity Surplus: "+str(np.round(surplus,2))+' GWh')
                                st.write("Water Surplus: "+str(np.round(w_sup,2))+' MIG')
                                
                                st.write('Electricity Generation Break-down')
                                df=pd.DataFrame({'Capacity (MW)':[capacity1,capacity21,capacity3,capacity4,capacity5], 'Annual Generation (GWh)':[ag1,ag2,ag3,ag4,ag5], 'Primary Energy (GWh)':[pe1,pe2,pe3,pe4,pe5]})
        
                                df=df.rename(index={0: "CCGT", 1: "SCGT", 2: "Coal", 3:"Ground-mount Solar", 4:"Distributed Rooftop Solar"})
                                st.dataframe(df.T)
                                csv_downloader(df,'Energy Generation Break-down')
                                st.write('Primary Energy Electricity Generation Summary')
                                df2=pd.DataFrame({'Gas':[ag1+ag2,pe1+pe2,(pe1+pe2)*btu_convert, gas_co2],'Coal':[ag3,pe3, pe3*btu_convert, coal_co2], 
                                                  'Solar':[ag4+ag5,pe4+pe5,(pe4+pe5)*btu_convert, solar_co2]})
                                df2=df2.rename({0:'Generation (GWh)' ,1:'Primary Energy (GWh)',2:'Primary Energy (Mbtu)',3:'Metric tons CO2'},axis='index')
                                st.dataframe(df2)   
                                csv_downloader(df2,'Primary Energy Electricity Generation Summary')
                                st.write('Solar Installation Area')
                                df3=pd.DataFrame({'Ground':[pe4/annual_insolation4 if annual_insolation4!=0 else 0],'Roof':[pe5/annual_insolation4 if annual_insolation4!=0 else 0]})
                                df3=df3.rename({0:"km{}".format('\u00B2')},axis='index')
                                st.dataframe(df3) 
                                csv_downloader(df3,'Solar Installation Area')
                                
                                st.write('Water Generation Break-down')
                                df4=pd.DataFrame({'Annual Generation (MIG)':[msf_water_generation,ro_water_generation], 
                                                  'Electricity Consumption (GWh)':[msf_e_con,ro_e_con],
                                                  'Heat Consumption (GWh)':[msf_heat_con,'NA']})
        
                                df4=df4.rename(index={0: "MSF", 1: "RO"})
                                st.dataframe(df4.T)
                                csv_downloader(df4,'Water Generation Break-down')
                                
                                if w_sup>=0:
                                    w_all=w_res+w_comm+w_ind+w_other+w_sup
                                    w_res_p=w_res/w_all if w_all!=0 else 0
                                    w_comm_p=w_comm/w_all if w_all!=0 else 0
                                    w_ind_p=w_ind/w_all if w_all!=0 else 0
                                    w_other_p=w_other/w_all if w_all!=0 else 0
                                    w_sup_p=w_sup/w_all if w_all!=0 else 0
                                    ##Sankey Diagram
                                    label=['Gas',
                                            'Coal',
                                            'Solar',
                                            'Distribute Rooftop Solar Ori',
                                            'CCGT',
                                            'SCGT',
                                            'Coal',
                                            'Ground-mount Solar',
                                            'Distributed Rooftop Solar',
                                            'Heat',
                                            'Electricity',
                                            'MSF',
                                            'RO',
                                            'Water',
                                            'Power & Water Auxillary',
                                            'Residential Electricity',
                                            'Commercial Electricity',
                                            'Industrial Electricity',
                                            'Other Electricity',
                                            'Exp.',
                                            'Residential Water',
                                            'Commercial Water',
                                            'Industrial Water',
                                            'Other Water',
                                            'Water Surplus',
                                            'Boiler Heat',
                                            'Nuclear'
                                            ]
                                    source=[0,0,1,2,2,
                                            4,4,5,6,7,8,26,
                                            9,25,10,10,10,10,10,10,10,10,
                                            12,11,
                                            13,13,13,13,13]
                                    target=[4,5,6,7,8,
                                           9,10,10,10,10,10,10,
                                           11,11,12,14,15,16,17,18,19,11,
                                           13,13,
                                           20,21,22,23,24]
                                    value=[pe1,pe2,pe3,pe4,pe5,
                                           msf_heat_con,ag1,ag2,ag3,ag4,ag5,nuclear_con,
                                           msf_heat_con,h_boiler,ro_e_con,e_aux,e_res,e_comm,e_ind,e_other,surplus,msf_e_con,
                                           ro_e_con,msf_heat_con+h_boiler,
                                           w_res_p*total_we_con,w_comm_p*total_we_con,w_ind_p*total_we_con,w_other_p*total_we_con, w_sup_p*total_we_con
                                          ]
                                    color_link=['#DEE3E9','#DEE3E9','#CBB4D5','lightsalmon','lightsalmon',
                                                'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                'lightpink','lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                '#A6E3D7','paleturquoise',
                                                'lightblue','lightblue','lightblue','lightblue','lightblue'
                                        
                                    ]
                                    color_node=['darkgrey','purple','salmon','salmon',
                                                'peachpuff','peachpuff','rosybrown','palevioletred','palevioletred',
                                                'lightpink','yellow','turquoise','cadetblue',
                                                'cadetblue',
                                                'olive','olive','olive','olive','olive','olive','deepskyblue','deepskyblue'
                                                ,'deepskyblue','deepskyblue','deepskyblue','lightpink','green','cadetblue','lightpink'
                                               ]
                                    
                                    link=dict(source=source,target=target,value=value, color=color_link)
                                    node=dict(label=label, pad=15, thickness=5, color=color_node)
                                    data=go.Sankey(link=link, node=node, arrangement='freeform')
                                    fig=go.Figure(data)
                                    fig.update_layout(hovermode='x',
                                                     title='Energy Flow Dubai',
                                                     font=dict(size=12,color='black'),)
                                    st.markdown('### Energy Sankey Diagram')
                                    st.plotly_chart(fig)
                                else:
                                    w_all=w_res+w_comm+w_ind+w_other
                                    w_res_p=w_res/w_all if w_all!=0 else 0
                                    w_comm_p=w_comm/w_all if w_all!=0 else 0
                                    w_ind_p=w_ind/w_all if w_all!=0 else 0
                                    w_other_p=w_other/w_all if w_all!=0 else 0
                                    ##Sankey Diagram
                                    label=['Gas',
                                            'Coal',
                                            'Solar',
                                            'Distribute Rooftop Solar Ori',
                                            'CCGT',
                                            'SCGT',
                                            'Coal',
                                            'Ground-mount Solar',
                                            'Distributed Rooftop Solar',
                                            'Heat',
                                            'Boiler Heat',
                                            'Electricity',
                                            'MSF',
                                            'RO',
                                            'Water',
                                            'Power & Water Auxillary',
                                            'Residential Electricity',
                                            'Commercial Electricity',
                                            'Industrial Electricity',
                                            'Other Electricity',
                                            'Exp.',
                                            'Residential Water',
                                            'Commercial Water',
                                            'Industrial Water',
                                            'Other Water',
                                            'Nuclear'
                                            ]
                                    source=[0,0,1,2,2,
                                            4,4,5,6,7,8,25,
                                            9,10,11,11,11,11,11,11,11,11,
                                            13,12,
                                            14,14,14,14]
                                    target=[4,5,6,7,8,
                                           9,11,11,11,11,11,11,
                                           12,12,13,15,16,17,18,19,20,12,
                                           14,14,
                                           21,22,23,24]
                                    
                                    value=[pe1,pe2,pe3,pe4,pe5,
                                           msf_heat_con,ag1,ag2,ag3,ag4,ag5,nuclear_con,
                                           msf_heat_con,h_boiler,ro_e_con,e_aux,e_res,e_comm,e_ind,e_other,surplus,msf_e_con,
                                           ro_e_con,msf_heat_con+h_boiler,
                                           w_res_p*total_we_con,w_comm_p*total_we_con,w_ind_p*total_we_con,w_other_p*total_we_con
                                          ]
                                    color_link=['#DEE3E9','#DEE3E9','#CBB4D5','lightsalmon','lightsalmon',
                                                'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                'lightpink','lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                '#A6E3D7','paleturquoise',
                                                'lightblue','lightblue','lightblue','lightblue'
                                        
                                    ]
                                    color_node=['darkgrey','purple','salmon','salmon',
                                                'peachpuff','peachpuff','rosybrown','palevioletred','palevioletred',
                                                'lightpink','lightpink','yellow','turquoise','cadetblue',
                                                'cadetblue',
                                                'olive','olive','olive','olive','olive','olive','deepskyblue','deepskyblue',
                                                'deepskyblue','deepskyblue','lightpink','green'
                                               ]
                                    link=dict(source=source,target=target,value=value, color=color_link)
                                    node=dict(label=label, pad=15, thickness=5, color=color_node)
                                    data=go.Sankey(link=link, node=node, arrangement='freeform')
                                    fig=go.Figure(data)
                                    fig.update_layout(hovermode='x',
                                                     title='Energy Flow Dubai',
                                                     font=dict(size=12,color='black'),)
                                    st.markdown('### Energy Sankey Diagram')
                                    st.plotly_chart(fig)
                                
                                #Generation Percentage
                                df2=df2[df2>0]
                                fig3=px.pie(df2, values=df2.loc['Generation (GWh)',:], names=df2.columns, hole=.3, color_discrete_sequence=px.colors.sequential.YlOrRd)
                                fig3.update_layout(
                                            title_text="Electricity Generation  (GWh)",
                                            # Add annotations in the center of the donut pies.
                                            annotations=[dict(text='Electricity', x=0.5, y=0.5, font_size=20, showarrow=False)])
                                st.plotly_chart(fig3)
                                
                                #CO2 Emission
                                ghg=pd.DataFrame({'Primary_Energy':['Natural Gas','Coal','Solar Embodied'],'CO2_Emission':[gas_co2,coal_co2,solar_co2]})
                                ghg=ghg[ghg.CO2_Emission>0]
                                fig2=px.pie(ghg, values=ghg.CO2_Emission, names=ghg.Primary_Energy, hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
                                fig2.update_layout(
                                            title_text="CO\u2082 Emissions (Metric tons)",
                                            # Add annotations in the center of the donut pies.
                                            annotations=[dict(text='CO\u2082', x=0.5, y=0.5, font_size=20, showarrow=False)])
                                st.plotly_chart(fig2)
                                
                                #Ｗater Generation
                                fig4=px.pie(df4.T, values=df4.T.loc['Annual Generation (MIG)',:], names=df4.T.columns, hole=.3, color_discrete_sequence=px.colors.sequential.Teal)
                                fig4.update_layout(
                                            title_text="Water Generation  (MIG)",
                                            # Add annotations in the center of the donut pies.
                                            annotations=[dict(text='Water', x=0.5, y=0.5, font_size=20, showarrow=False)])
                                st.plotly_chart(fig4)
                                
                       
                elif task=='DEWA':
                    st.header('Scenarios')
                    e_file=st.file_uploader('Electricity Generation Data',type=['csv','txt','xlsx'])
                    if e_file:
                        edf=pd.read_csv(e_file,thousands=',')
                        st.dataframe(edf)   
                    e_confile=st.file_uploader('Electricity Consumption Data',type=['csv','txt','xlsx'],accept_multiple_files=True)
                    if e_confile:
                        econdf=[]
                        for file in e_confile:
                            econ_file=pd.read_csv(file,thousands=',')
                            file.seek(0)
                            econdf.append(econ_file)
                        econdf=pd.concat(econdf)
                        st.dataframe(econdf) 
                    e_statistics=st.file_uploader('DEWA Annual Statistics',type=['csv','txt','xlsx'])
                    if e_statistics:
                        statisticdf=pd.read_csv(e_statistics, thousands=',')
                        st.dataframe(statisticdf)
                    w_file=st.file_uploader('Water Production Data',type=['csv','txt','xlsx'])
                    if w_file:
                        wdf=pd.read_csv(w_file, thousands=',')
                        st.dataframe(wdf)
                    if e_file and w_file:
                        st.header('Water')
                        msf_production=wdf.iloc[:,[2,3,4,5,6,7]].sum().sum()
                        st.write('MSF Production: '+str(msf_production)+ " MIG")
                        ro_production=wdf.iloc[:,[8,9]].sum().sum()
                        st.write('RO Production: '+str(ro_production)+ " MIG")
                        desal_heat2=st.number_input("Desalination Heat Demand (kWh/m3)",60) 
                        desal_heat3=st.number_input("Desalination (MSF) Electrcity Demand (kWh/m3)",3)
                        desal_heat4=st.number_input("Desalination (RO) Electrcity Demand (kWh/m3)",3)
                        msf_heat_con=msf_production*desal_heat2*4546/1000000
                        msf_e_con=msf_production*desal_heat3*4546/1000000
                        ro_e_con=ro_production*desal_heat4*4546/1000000
                        #col1,col2=st.beta_columns([2,1])
                        #with col1:
                        st.header('Electricity')
                        st.subheader('CCGT')
                        ag1=edf.iloc[:,[2,3,4,6,7,8]].sum().sum()/1000
                        cap1=np.round(ag1/(capacity['Jabel Ali']*1000*12),2)*100
                        st.write("Generation: "+str(ag1)+' MWh')
                        st.write("Capacity Factor: "+str(cap1)+' %')
                        thermal_efficiency2=st.number_input("Thermal Efficiency % (CCGT)",float(0),float(500000000000),82.0,0.1)
                        efficiency1=efficiency('Jabel Ali',cap1,ag1,thermal_efficiency2,msf_production,desal_heat2)
                        #with col2:
                        st.subheader('SCGT')
                        ag2=edf.iloc[:,5].sum()/1000
                        cap2=np.round(ag2/(capacity['Al Aweer']*1000*12),2)*100
                        st.write("Generation: "+str(ag2)+' MWh')
                        st.write("Capacity Factor: "+str(cap2)+' %')
                        efficiency2=st.number_input("Efficiency % (SCGT)",33)
                        
                        st.subheader('COAL')
                        ag3=edf.iloc[:,5].sum()/1000
                        cap3=np.round(ag3/(capacity['Hassyan']*1000*12),2)*100
                        st.write("Generation: "+str(ag3)+' MWh')
                        st.write("Capacity Factor: "+str(cap3)+' %')
                        efficiency3=st.number_input("Efficiency % (Hassyan)",40)
                    
                        st.subheader('GMPV')
                        ag4=edf.iloc[:,[9,10]].sum().sum()/1000
                        cap4=np.round(ag4/(capacity['MBR Solar']*1000*12),2)*100
                        st.write("Generation: "+str(ag2)+' MWh')
                        st.write("Capacity Factor: "+str(cap4)+' %')
                        annual_insolation4=st.number_input("Annual Insolation (kWh/m2)",float(0),float(500000000000),2100.0,0.1)
                        land_area4=st.number_input("Land Area (km2)",15)
                        epbt=st.number_input("Energy Payback Time",0) 
                        efficiency4=efficiency('MBR Solar',cap4,ag4,thermal_efficiency2,msf_production,annual_insolation=annual_insolation4,land=land_area4)
                        efficiency4_1=(ag4)/(annual_insolation4*land_area4)
                        pe1=(msf_heat_con+ag1)/efficiency1 if efficiency1!=0 else 0
                        pe2=(ag2)/(efficiency2/100) if efficiency2!=0 else 0
                        pe4=(ag4)/efficiency4_1 if efficiency4!=0 else 0
                        
                        #co2 calculation 
                        gas_co2=(pe1+pe2)*btu_convert*co2_factor['natural_gas']
                        #coal_co2=pe3*btu_convert*co2_factor['coal']
                        solar_co2=((epbt)/25)*0.09*btu_convert*(ag4)
                        
                        st.subheader('Electricity Generation Break-down')
                        df1=pd.DataFrame({'Annual Generation (GWh)':[ag1,ag2,ag4], 'Primary Energy (GWh)':[pe1,pe2,pe4]})

                        df1=df1.rename(index={0: "CCGT", 1: "SCGT", 2:"GMPV"})
                        st.dataframe(df1.T)
                        csv_downloader(df1,'Energy Generation Break-down')
                        
                        st.write('Primary Energy Summary')
                        df2=pd.DataFrame({'Gas':[ag1+ag2,pe1+pe2,(pe1+pe2)*btu_convert,gas_co2],'Solar':[ag4, pe4, pe4*btu_convert, solar_co2]})
                        df2=df2.rename({0:'Generation (GWh)' ,1:'Primary Energy (GWh)',2:'Primary Energy (Mbtu)',3:'Metric tons CO2'},axis='index')
                        st.dataframe(df2)
                        csv_downloader(df2,'Primary Energy Summary')
                        
                        e_aux=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Auxilary')]['value'].values
                        e_res=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Residential')]['value'].values
                        e_comm=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Commercial')]['value'].values
                        e_ind=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Industrial')]['value'].values
                        e_other=statisticdf.loc[(statisticdf.item_name=='Electricity Consumption') & (statisticdf.type=='Others')]['value'].values
                        w_all=statisticdf.loc[statisticdf.item_name=='Total System Required (Desalination Water Demand)']['value'].values
                        total_w_con=statisticdf.loc[statisticdf.item_name=='Water Consumption']['value'].astype(int).sum()
                        w_res_p=int(statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Residential')]['value'].values)/int(total_w_con)
                        w_comm_p=int(statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Commercial')]['value'].values)/int(total_w_con)
                        w_ind_p=int(statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Industrial')]['value'].values)/int(total_w_con)
                        w_other_p=int(statisticdf.loc[(statisticdf.item_name=='Water Consumption') & (statisticdf.type=='Others')]['value'].values)/int(total_w_con)
                        total_we_con=ro_e_con+msf_heat_con+msf_e_con
                        
                        ##Sankey Diagram
                        label=['Gas',
                                'Solar',
                                'CCGT',
                                'SCGT',
                                'GMPV',
                                'Heat',
                                'Electricity',
                                'MSF',
                                'RO',
                                'Water',
                                'Residential Water',
                                'Commercial Water',
                                'Industrial Water',
                                'Other Water',
                                'Exp.',
                                'Power & Water Auxillary Electricity',
                                'Residential Electricity',
                                'Commercial Electricity',
                                'Industrial Electricity',
                                'Other Electricity',
                                'Carbon Dioxide Emission',
                                ]
                        source=[
                                0,0,1,
                                2,2,3,4,
                                5,6,6,6,6,6,6,6,
                                7,8,
                                9,9,9,9]
                        target=[
                               2,3,4,
                               5,6,6,6,
                               7,7,8,15,16,17,18,19,
                               9,9,
                               10,11,12,13]
                        value=[
                               pe1,pe2,pe4,
                               msf_heat_con,ag1,ag2,ag4,
                               msf_heat_con,msf_e_con,ro_e_con,e_aux,e_res,e_comm,e_ind,e_other,
                               msf_heat_con+msf_e_con,ro_e_con,
                               w_res_p*total_we_con,w_comm_p*total_we_con,w_ind_p*total_we_con,w_other_p*total_we_con
                               ]
                        
                        color_link=[
                                    '#DEE3E9','#DEE3E9','lightsalmon',
                                    'lightpink','#FEF3C7','#FEF3C7','#FEF3C7',
                                    'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                    'lightblue','lightblue',
                                    'lightblue','lightblue','lightblue','lightblue'
                            
                        ]
                        color_node=['darkgrey','salmon',
                                    'peachpuff','peachpuff','palevioletred','lightpink','yellow','turquoise','turquoise',
                                    'cadetblue','deepskyblue','deepskyblue','deepskyblue','deepskyblue',
                                    'olive','olive','olive','olive','olive','olive','cadetblue','black',
                                   ]
                        link=dict(source=source,target=target,value=value, color=color_link)
                        node=dict(label=label, pad=15, thickness=5, color=color_node)
                        data=go.Sankey(link=link, node=node, arrangement='freeform')
                        fig=go.Figure(data)
                        fig.update_layout(hovermode='x',
                                         title='Energy Flow Dubai',
                                         font=dict(size=12,color='black'),)
                        st.markdown('### Energy Sankey Diagram')
                        st.plotly_chart(fig)
                        
                        #Generation Percentage
                        df2=df2[df2>0]
                        fig3=px.pie(df2, values=df2.loc['Generation (GWh)',:], names=df2.columns, hole=.3, color_discrete_sequence=px.colors.sequential.YlOrRd)
                        fig3.update_layout(
                                    title_text="Electricity Generation (GWh)",
                                    # Add annotations in the center of the donut pies.
                                    annotations=[dict(text='Electricity', x=0.5, y=0.5, font_size=20, showarrow=False)])
                        st.plotly_chart(fig3)
                                
                        #co2 emission 
                        ghg=pd.DataFrame({'Primary_Energy':['Natural Gas','Solar Embodied'],'CO2_Emission':[gas_co2,solar_co2]})
                        ghg=ghg[ghg.CO2_Emission>0]
                        fig2=px.pie(ghg, values=ghg.CO2_Emission, names=ghg.Primary_Energy, hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
                        fig2.update_layout(
                                    title_text="CO\u2082 Emissions (Metric tons)",
                                    # Add annotations in the center of the donut pies.
                                    annotations=[dict(text='CO\u2082', x=0.5, y=0.5, font_size=20, showarrow=False)])
                        st.plotly_chart(fig2)
                        
                        #Ｗater Generation
                        df4=pd.DataFrame({'Annual Generation (MIG)':[msf_production,ro_production], 
                                        'Electricity Consumption (GWh)':[msf_e_con,ro_e_con],
                                        'Heat Consumption (GWh)':[msf_heat_con,'NA']})
                        df4=df4.rename(index={0: "MSF", 1: "RO"})
                        fig4=px.pie(df4.T, values=df4.T.loc['Annual Generation (MIG)',:], names=df4.T.columns, hole=.3, color_discrete_sequence=px.colors.sequential.Teal)
                        fig4.update_layout(
                                    title_text="Water Generation  (MIG)",
                                    # Add annotations in the center of the donut pies.
                                    annotations=[dict(text='Water', x=0.5, y=0.5, font_size=20, showarrow=False)])
                        st.plotly_chart(fig4)
                    else:
                        original_title = '<p style="font-family:Courier; color:Red; font-size: 20px;">Please upload the generation and production file</p>'
                        st.markdown(original_title, unsafe_allow_html=True)
                
                    #st.write("Technology: CCGT", ", Capacity: "+str(capacity1)+' (MW/MIGD)')
                        #col1,col2=st.beta_columns([2,1])
                        #with col1:
                            #cf1=st.number_input("Capacity Factor % (CCGT)")
                        #with col2:
                            #thermal_efficiency1=st.number_input("Thermal Efficiency % (CCGT)")
                    
                elif task=="DEWA Test Case":
                    st.header("Dubai Energy Flow Variables")
                    with st.form(key='consumption records'):
                        st.subheader('Electricity Consumption (GWh)')
                        col1,col2,col3=st.beta_columns([3,2,1])
                        with col1:
                            e_res=st.number_input("Residential")
                            e_comm=st.number_input("Commercial")
                            e_aux=st.number_input("Power & Water Auxillary")
                        with col2:
                            e_ind=st.number_input("Industrial")
                            e_other=st.number_input("Other")
                        st.write("DEWA Reported Consumption")
                        reported_e=st.number_input("Reported Electricity Consumption (GWh)")
                        
                        st.subheader('Water Consumption (MIG)')
                        col1,col2,col3=st.beta_columns([3,2,1])
                        with col1:
                            w_res=st.number_input("Residential Water")
                            w_comm=st.number_input("Commercial Water")
                        with col2:
                            w_ind=st.number_input("Industrial Water")
                            w_other=st.number_input("Other Water")
                        st.write("DEWA Reported Consumption")
                        reported_w=st.number_input("Reported Water Consumption (MIG)")
                            
                        submit_button4=st.form_submit_button(label='Save')
                        if submit_button4:
                            st.write("Your consumption records have been saved")
                    with st.form(key='form1'):
                        st.subheader('Jebel Ali')
                        capacity1=capacity['Jabel Ali']
                        st.write("Technology: CCGT", ", Capacity: "+str(capacity1)+' (MW/MIGD)')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf1=st.number_input("Capacity Factor % (CCGT)")
                            cad1=st.number_input("CCGT Capacity Adjustment (MW)")
                            capacity1+=cad1
                            
                        with col2:
                            thermal_efficiency1=st.number_input("Thermal Efficiency % (CCGT)")
                        
                        st.subheader('Jebel Ali Desalination Plant')
                        st.write("Desalination Plant MSF")
                        thermal_e=st.number_input("Thermal to Electric Factor")
                        desal_heat1=st.number_input("Desalination Heat Demand (kWh/m3)")/220
                        desal_elec_msf_1=st.number_input("MSF Desalination Electricity Demand (kWh/m3)")/220
                        st.write("Desalination Plant RO")
                        desal_elec_ro_1=st.number_input("RO Desalination Electricity Demand (kWh/m3)")/220
                            
                        
                        st.subheader('Al Aweer')
                        capacity2=capacity['Al Aweer']
                        st.write("Technology: SCGT", ", Capacity: "+str(capacity2)+' (MW)')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf2=st.number_input("Capacity Factor % (SCGT)")
                            cad2=st.number_input("SCGT Capacity Adjustment (MW)")
                            capacity2+=cad2
                        with col2:
                            efficiency2=st.number_input("Efficiency % (SCGT)")
                        

                        st.subheader('Hassyan')
                        capacity3=capacity['Hassyan']
                        st.write("Technology: USC Coal",", Capacity: "+str(capacity3)+' (MW)')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf3=st.number_input("Capacity Factor % (USC Coal)")
                            cad3=st.number_input("USC Coal Capacity Adjustment (MW)")
                            capacity3+=cad3
                            st.write("Technology: USC Coal",", Capacity: "+str(capacity3)+' (MW)')
                        with col2:
                            efficiency3=st.number_input("Efficiency % (USC Coal)")
                        
                            
                        st.subheader('MBR Solar')
                        capacity4=capacity['MBR Solar']
                        st.write("Technology: Ground-mount PV",", Capacity: "+str(capacity4)+' (MW)')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf4=st.number_input("Capacity Factor % (Ground-mount PV)")
                            cad4=st.number_input("Ground-mount PV Capacity Adjustment (MW)")
                            capacity4+=cad4
                            epbt=st.number_input("Energy Payback Time") 
                            epbt=epbt if epbt!=0 else  1
                        with col2:
                            annual_insolation4=st.number_input("Annual Insolation (kWh/m2)")
                            land_area4=st.number_input("Land Area (km2)")
                        
                        st.subheader('Shams Dubai')
                        capacity5=capacity['Shams Dubai']
                        st.write("Technology: Distribued Rooftop PV",", Capacity: "+str(capacity5)+' (MW)')
                        col1,col2=st.beta_columns([2,1])
                        with col1:
                            cf5=st.number_input("Capacity Factor % (Distribued Rooftop PV)")
                            cad5=st.number_input("Distribued Rooftop PV Capacity Adjustment (MW)")
                            capacity5+=cad5
                        with col2:
                            efficiency5=st.number_input("Efficiency %(Distribued Rooftop PV)")
                        
                        submit_button=st.form_submit_button(label="Submit")
                        if submit_button:
                            st.write("Your input has been submitted. Results are calculated below")
                            with st.beta_expander("Results"):
                                ag1=annual_generation(capacity1, cf1, 'Electricity')
                                ag2=annual_generation(capacity2, cf2, 'Electricity')
                                ag3=annual_generation(capacity3, cf3, 'Electricity')
                                ag4=annual_generation(capacity4, cf4, 'Electricity')
                                ag5=annual_generation(capacity5, cf5, 'Electricity')
                                desal_cf=water_cf(reported_w,470)
                                #msf_water_generation=annual_generation(445, desal_cf, 'Water')
                                msf_heat_con=thermal_e*ag1
                                msf_water_generation=msf_heat_con/heat_convert
                                #msf_e_con=msf_water_generation*e_convert
                                msf_e_con=msf_water_generation/desal_elec_msf_1
                                ro_water_generation=annual_generation(25, desal_cf, 'Water')
                                #ro_e_con=ro_water_generation*e_convert
                                ro_e_con=ro_water_generation*desal_elec_ro_1
                                total_we_con=ro_e_con+msf_heat_con+msf_e_con
                                w_sup=reported_w-msf_water_generation-ro_water_generation
                                
                                efficiency1=efficiency('Jabel Ali',cf1,ag1,thermal_efficiency1,msf_water_generation,desal_heat1)
                                efficiency4=efficiency('MBR Solar',cf4,ag4,thermal_efficiency1,msf_water_generation,desal_heat1,annual_insolation4,land=land_area4)
                                pe1=ag1/efficiency1 if efficiency1!=0 else 0
                                pe2=ag2/(efficiency2/100) if efficiency2!=0 else 0
                                pe3=ag3/(efficiency3/100) if efficiency3!=0 else 0
                                pe4=ag4/efficiency4 if efficiency4!=0 else 0
                                pe5=ag5/(efficiency5/100) if efficiency5!=0 else 0
                                
                                #co2 calculation 
                                gas_co2=(pe1+pe2)*btu_convert*co2_factor['natural_gas']
                                coal_co2=pe3*btu_convert*co2_factor['coal']
                                solar_co2=((epbt)/25)*0.09*btu_convert*(ag4+ag5)
                                
                                st.write('Electricity Generation Break-down')
                                df=pd.DataFrame({'Adjusted Capacity':[capacity1,capacity2,capacity3,capacity4,capacity5], 'Annual Generation':[ag1,ag2,ag3,ag4,ag5], 'Primary Energy':[pe1,pe2,pe3,pe4,pe5]})
        
                                df=df.rename(index={0: "Jabel Ali", 1: "Al Aweer", 2: "Hassyan", 3:"MBR Solar", 4:"Shams Dubai"})
                                st.dataframe(df.T)
                                csv_downloader(df,'Energy Generation Break-down')
                                st.write('Primary Energy Electricity Generation Summary')
                                df2=pd.DataFrame({'Gas':[ag1+ag2,pe1+pe2,(pe1+pe2)*btu_convert, gas_co2],'Coal':[ag3,pe3, pe3*btu_convert, coal_co2], 'GM Solar':[ag4,pe4, pe4*btu_convert, ((epbt)/25)*0.09*btu_convert*ag4],
                                                  'RFTP Solar':[ag5, pe5, pe5*btu_convert, ((epbt)/25)*0.09*btu_convert*ag5], 'Solar':[ag4+ag5,pe4+pe5,(pe4+pe5)*btu_convert, solar_co2]})
                                df2=df2.rename({0:'Generation (GWh)' ,1:'Primary Energy (GWh)',2:'Primary Energy (Mbtu)',3:'Metric tons CO2'},axis='index')
                                st.dataframe(df2)   
                                csv_downloader(df2,'Primary Energy Electricity Generation Summary')
                                st.write('Solar Installation Area')
                                df3=pd.DataFrame({'Ground':[pe4/annual_insolation4 if annual_insolation4!=0 else 0],'Roof':[pe5/annual_insolation4 if annual_insolation4!=0 else 0]})
                                df3=df3.rename({0:"km{}".format('\u00B2')},axis='index')
                                st.dataframe(df3) 
                                csv_downloader(df3,'Solar Installation Area')
                                surplus=ag1+ag2+ag3+ag4+ag5-reported_e
                                st.write("Electricity Surplus: "+str(np.round(surplus,2))+' GWh')
                                
                                if w_sup>0:
                                    w_all=w_res+w_comm+w_ind+w_other
                                    w_res_p=w_res/w_all if w_all!=0 else 0
                                    w_comm_p=w_comm/w_all if w_all!=0 else 0
                                    w_ind_p=w_ind/w_all if w_all!=0 else 0
                                    w_other_p=w_other/w_all if w_all!=0 else 0
                                    w_sup_p=w_sup/w_all if w_all!=0 else 0
                                    ##Sankey Diagram
                                    label=['Gas',
                                            'Coal',
                                            'Ground Solar',
                                            'Rooftop Solar',
                                            'Jabel Ali',
                                            'Al Aweer',
                                            'Hassyan',
                                            'MBR Solar',
                                            'Shams Dubai',
                                            'Heat',
                                            'Electricity',
                                            'MSF',
                                            'RO',
                                            'Water',
                                            'Power & Water Auxillary',
                                            'Residential Electricity',
                                            'Commercial Electricity',
                                            'Industrial Electricity',
                                            'Other Electricity',
                                            'Exp.',
                                            'Residential Water',
                                            'Commercial Water',
                                            'Industrial Water',
                                            'Other Water',
                                            'Water Surplus'
                                            'Carbon Dioxide Emission'
                                            ]
                                    source=[
                                            0,0,1,2,3,
                                            4,4,5,6,7,8,
                                            9,10,10,10,10,10,10,10,10,
                                            12,11,
                                            13,13,13,13,13]
                                    target=[
                                           4,5,6,7,8,
                                           9,10,10,10,10,10,
                                           11,12,14,15,16,17,18,19,11,
                                           13,13,
                                           20,21,22,23,24]
                                    value=[
                                           pe1,pe2,pe3,pe4,pe5,
                                           msf_heat_con,ag1,ag2,ag3,ag4,ag5,
                                           msf_heat_con,ro_e_con,e_aux,e_res,e_comm,e_ind,e_other,surplus,msf_e_con,
                                           ro_e_con,msf_heat_con,
                                           w_res_p*total_we_con,w_comm_p*total_we_con,w_ind_p*total_we_con,w_other_p*total_we_con, w_sup_p*total_we_con
                                          ]
                                    color_link=[
                                                '#DEE3E9','#DEE3E9','#CBB4D5','lightsalmon','lightsalmon',
                                                'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                '#A6E3D7','paleturquoise',
                                                'lightblue','lightblue','lightblue','lightblue','lightblue'
                                        
                                    ]
                                    color_node=[
                                                'darkgrey','purple','salmon','salmon',
                                                'peachpuff','peachpuff','rosybrown','palevioletred','palevioletred',
                                                'lightpink','yellow','turquoise','cadetblue',
                                                'cadetblue',
                                                'olive','olive','olive','olive','olive','olive','deepskyblue','deepskyblue'
                                                ,'deepskyblue','deepskyblue','deepskyblue','Black'
                                               ]
                                    link=dict(source=source,target=target,value=value, color=color_link)
                                    node=dict(label=label, pad=15, thickness=5, color=color_node)
                                    data=go.Sankey(link=link, node=node, arrangement='freeform')
                                    fig=go.Figure(data)
                                    fig.update_layout(hovermode='x',
                                                     title='Energy Flow Dubai',
                                                     font=dict(size=12,color='black'),)
                                    st.markdown('### Energy Sankey Diagram')
                                    st.plotly_chart(fig)
                                else:
                                    w_all=w_res+w_comm+w_ind+w_other
                                    w_res_p=w_res/w_all if w_all!=0 else 0
                                    w_comm_p=w_comm/w_all if w_all!=0 else 0
                                    w_ind_p=w_ind/w_all if w_all!=0 else 0
                                    w_other_p=w_other/w_all if w_all!=0 else 0
                                    ##Sankey Diagram
                                    label=['Gas',
                                            'Coal',
                                            'Ground Solar',
                                            'Rooftop Solar',
                                            'Jabel Ali',
                                            'Al Aweer',
                                            'Hassyan',
                                            'MBR Solar',
                                            'Shams Dubai',
                                            'Heat',
                                            'Electricity',
                                            'MSF',
                                            'RO',
                                            'Water',
                                            'Power & Water Auxillary',
                                            'Residential Electricity',
                                            'Commercial Electricity',
                                            'Industrial Electricity',
                                            'Other Electricity',
                                            'Exp.',
                                            'Residential Water',
                                            'Commercial Water',
                                            'Industrial Water',
                                            'Other Water',
                                            'Carbon Dioxide Emission'
                                            ]
                                    source=[
                                            0,0,1,2,3,
                                            4,4,5,6,7,8,
                                            9,10,10,10,10,10,10,10,10,
                                            12,11,
                                            13,13,13,13]
                                    target=[
                                           4,5,6,7,8,
                                           9,10,10,10,10,10,
                                           11,12,14,15,16,17,18,19,11,
                                           13,13,
                                           20,21,22,23]
                                    value=[
                                           pe1,pe2,pe3,pe4,pe5,
                                           msf_heat_con,ag1,ag2,ag3,ag4,ag5,
                                           msf_heat_con,ro_e_con,e_aux,e_res,e_comm,e_ind,e_other,surplus,msf_e_con,
                                           ro_e_con,msf_heat_con,
                                           w_res_p*total_we_con,w_comm_p*total_we_con,w_ind_p*total_we_con,w_other_p*total_we_con
                                          ]
                                    color_link=[
                                                '#DEE3E9','#DEE3E9','#CBB4D5','lightsalmon','lightsalmon',
                                                'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                'lightpink','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7','#FEF3C7',
                                                '#A6E3D7','paleturquoise',
                                                'lightblue','lightblue','lightblue','lightblue'
                                        
                                    ]
                                    color_node=[
                                                'darkgrey','purple','salmon','salmon',
                                                'peachpuff','peachpuff','rosybrown','palevioletred','palevioletred',
                                                'lightpink','yellow','turquoise','cadetblue',
                                                'cadetblue',
                                                'olive','olive','olive','olive','olive','olive','deepskyblue','deepskyblue'
                                                ,'deepskyblue','deepskyblue','Black'
                                               ]
                                    link=dict(source=source,target=target,value=value, color=color_link)
                                    node=dict(label=label, pad=15, thickness=5, color=color_node)
                                    data=go.Sankey(link=link, node=node, arrangement='freeform')
                                    fig=go.Figure(data)
                                    fig.update_layout(hovermode='x',
                                                     title='Energy Flow Dubai',
                                                     font=dict(size=12,color='black'),)
                                    st.markdown('### Energy Sankey Diagram')
                                    st.plotly_chart(fig)
                                    
                                #Generation Percentage
                                fig3=px.pie(df2, values=df2.loc['Generation (GWh)',:], names=df2.columns, hole=.3, color_discrete_sequence=px.colors.sequential.Teal)
                                fig3.update_layout(
                                            title_text="Electricity Generation",
                                            # Add annotations in the center of the donut pies.
                                            annotations=[dict(text='Electricity', x=0.5, y=0.5, font_size=20, showarrow=False)])
                                st.plotly_chart(fig3)
                                
                                #CO2 Emission
                                ghg=pd.DataFrame({'Primary_Energy':['Natural Gas','Coal','Solar Embodied'],'CO2_Emission':[gas_co2,coal_co2,solar_co2]})
                                fig2=px.pie(ghg, values=ghg.CO2_Emission, names=ghg.Primary_Energy, hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
                                fig2.update_layout(
                                            title_text="CO\u2082 Emissions (Metric tons)",
                                            # Add annotations in the center of the donut pies.
                                            annotations=[dict(text='CO\u2082', x=0.5, y=0.5, font_size=20, showarrow=False)])
                                st.plotly_chart(fig2)
                elif task=="Summary":
                    st.header('Analytics')
                    
            else:
                st.warning("Incorrect Username/Password")
        #if st.sidebar.button("Logout"):
            #st.success("You have successfully logged out from the platform")
                
    elif action=="Sign up":
        st.write("### Create New Account")
        new_username=st.text_input("Username")
        new_password=st.text_input("Password", type='password')
            
        if st.button("Signup"):
            create_usertable()
            add_userdata(new_username,make_hashes(new_password))
            st.success("You have successfully created an account")
            st.info("Please login from the login menu")
if __name__=='__main__':
    main()
