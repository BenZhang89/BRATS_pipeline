##!usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import os,glob,shutil
import time
import pathlib

def filter_series(SeriesDescription,series_mapping,move=False,keep_exist=False,series_num=0):
    if any(x in SeriesDescription for x in ["AX_T1_PRE","AX_T1"]) and not "post" in SeriesDescription.lower():  #["t1", "pre"]
        seriesname='t1'
    elif any(x in SeriesDescription for x in ["AX_T2","SAG_T2_SPACE","3D_T2_SPACE",
                                              "BRAIN_MAPPING_T2_SPACE","SAG_3D_T2",
                                              "Head_AX_PD_T2"]) and not "recon" in SeriesDescription.lower(): #"SAG_3D_T2" leads to uncoregistration
        seriesname='t2'
        #"AX_T2_RECON_3MM", is a candidate
    elif any(x in SeriesDescription for x in ["SAG_3D_FLAIR","CS_3D_FLAIR_SPACE",
                                              "BRAIN_MAPPING_FLAIR_SPACE","SAG_FLAIR_SPACE",
                                              "3D_FLAIR_SPACE","SAG_SPACE_FLAIR","SAG_3D_FLAIR_SPACE",
                                              "SPACE_FLAIR","SAG_SPACE_FLAIR_256_FOV","SPACE_3D_FLAIR",
                                              "SAG_FLAIR_SPACE_(if_no_SPACE_then_SAG_FLAIR)",
                                              "AX_FLAIR"]) and not "recon" in SeriesDescription.lower():
        seriesname='flair'
    elif any(x in SeriesDescription for x in ["SAG_MPR","AX_3D_MPR","AX_MPR_FBH",
                                              "SAG_3D_MPR",
                                              "SAG_CS_MPRAGE"]) and not "recon" in SeriesDescription.lower(): #and series_num>100: #["3d", "mpr", "ax"]
        seriesname='t1ce'
    elif any(x in SeriesDescription.lower() for x in ["perfusion"]):
        seriesname='perfusion'
    else:
        return SeriesDescription, series_mapping, move, keep_exist, 'Notwant'

    # if series_mapping[seriesname] is same,i.e continue to route DICOMS since last filtering, move=True
    if series_mapping[seriesname] == SeriesDescription:
        move = True
        keep_exist = True
    # if series_mapping[seriesname] isn't a better choice, move=False
    elif series_mapping[seriesname] in ["AX_T1_PRE",
                                      "SAG_3D_FLAIR","CS_3D_FLAIR_SPACE",
                                      "BRAIN_MAPPING_FLAIR_SPACE","SAG_FLAIR_SPACE",
                                      "3D_FLAIR_SPACE","SAG_SPACE_FLAIR","SAG_3D_FLAIR_SPACE",
                                      "SPACE_FLAIR","SAG_SPACE_FLAIR_256_FOV","SPACE_3D_FLAIR",
                                      "SAG_FLAIR_SPACE_(if_no_SPACE_then_SAG_FLAIR)"]: #"SAG_3D_FLAIR_CS" lead core. issue
        move = False

    # if series_mapping[seriesname] is a better choice, move=True
    else:
        #if there is more than one series meet the condition, choose the one with less name
        #because longname is reconed,or edited after.
        if len(SeriesDescription) < len(series_mapping[seriesname]) or series_mapping[seriesname]=="AX_FLAIR":
            series_mapping[seriesname] = SeriesDescription
            move = True
            keep_exist = False

    return SeriesDescription, series_mapping, move, keep_exist, seriesname

# classify a series to 4 folders, i.e t1, t1ce,t2, flair
def classifydicom(acc_dir,logdate_dir,mod_op):
    print(f'Process this case {acc_dir}')
    acc = os.path.basename(acc_dir)
    logfile = os.path.join(logdate_dir,f"{acc}" + ".json")
    # dump a log dics first time
    if not os.path.exists(logfile):
        series_mapping = {'t1':"#"*100,'flair':"#"*100,'t2':"#"*100,'t1ce':"#"*100,'Notwant':"#"*100,'perfusion':"#"*100}
        log_json = open(logfile, "w")
        json.dump(series_mapping, log_json)
        log_json.close()
    # read logs
    log_json = open(logfile, "r")
    series_mapping = json.load(log_json)

    all_series = []

    
    print('-'.join(os.listdir(acc_dir)).lower())
    if mod_op==preop_bn:
        for SeriesDescription in os.listdir(acc_dir):
            if SeriesDescription not in ['t1','t1ce','t2','flair'] and os.path.isdir(os.path.join(acc_dir,SeriesDescription)):
                all_series.append(SeriesDescription)
                num_dicoms = len(os.listdir(os.path.join(acc_dir,SeriesDescription)))
                print(f'Process this series "{SeriesDescription}" in the {acc}, having {num_dicoms} dicoms')
                ##check whether the series meets the input requirement
                SeriesDescription, series_mapping, move, keep_exist, seriesname = filter_series(SeriesDescription,
                                                                            series_mapping,
                                                                            move=False,
                                                                            keep_exist=False,
                                                                            series_num=num_dicoms
                                                                                      )

                if seriesname!="Notwant" and move:
                    dst = os.path.join(acc_dir, seriesname)
                    # remove the existing series if find a better series
                    if not keep_exist:
                        if os.path.exists(dst):
                            shutil.rmtree(dst)

                    os.makedirs(dst,exist_ok = True)
                    for src_dicom in glob.glob(os.path.join(acc_dir,SeriesDescription,"*.dcm")):
                        # move dicoms to the subdicomdir
                        dst_dicom = os.path.join(dst,os.path.basename(src_dicom))
                        shutil.move(src_dicom, dst_dicom)

                    # update the log dic
                    log_json = open(logfile, "w")
                    json.dump(series_mapping, log_json)
                    log_json.close()
                    
    #only filter the study with perfusion for post op
    if mod_op==postop_bn:
        if "perfusion" in '-'.join(os.listdir(acc_dir)).lower():
            for SeriesDescription in os.listdir(acc_dir):
                if SeriesDescription not in ['t1','t1ce','t2','flair','perfusion'] and os.path.isdir(os.path.join(acc_dir,SeriesDescription)):
                    all_series.append(SeriesDescription)
                    num_dicoms = len(os.listdir(os.path.join(acc_dir,SeriesDescription)))
                    print(f'Process this series "{SeriesDescription}" in the {acc}, having {num_dicoms} dicoms')
                    ##check whether the series meets the input requirement
                    SeriesDescription, series_mapping, move, keep_exist, seriesname = filter_series(SeriesDescription,
                                                                                series_mapping,
                                                                                move=False,
                                                                                keep_exist=False,
                                                                                series_num=num_dicoms
                                                                                          )

                    if seriesname!="Notwant" and move:
                        dst = os.path.join(acc_dir, seriesname)
                        # remove the existing series if find a better series
                        if not keep_exist:
                            if os.path.exists(dst):
                                shutil.rmtree(dst)

                        os.makedirs(dst,exist_ok = True)
                        for src_dicom in glob.glob(os.path.join(acc_dir,SeriesDescription,"*.dcm")):
                            # move dicoms to the subdicomdir
                            dst_dicom = os.path.join(dst,os.path.basename(src_dicom))
                            shutil.move(src_dicom, dst_dicom)

                        # update the log dic
                        log_json = open(logfile, "w")
                        json.dump(series_mapping, log_json)
                        log_json.close()

#get the environment arguments
preop_dir = os.environ['preop_dir']
postop_dir = os.environ['postop_dir']
preop_bn = os.path.basename(preop_dir)
postop_bn = os.path.basename(postop_dir)
log_dir = os.environ['log_dir']
# dst_dir = os.environ['dst_dir']
#loopover the received DICOM that day
while True:
    for src_op_dir in [preop_dir,postop_dir]:
        mod_op = os.path.basename(src_op_dir)
        #remove all the received DICOMs one week ago
        week_ago = datetime.date.today() - datetime.timedelta(days=7)
        remove_date_dir = os.path.join(src_op_dir,f"{week_ago}")
        if os.path.exists(remove_date_dir):
            shutil.rmtree(remove_date_dir)
        #create log folder by date
        curdate = datetime.date.today() - datetime.timedelta(days=0) 
        logdate_dir = os.path.join(log_dir,mod_op,f"{curdate}")
        pathlib.Path(logdate_dir).mkdir(parents=True, exist_ok=True)

        today_dir = os.path.join(src_op_dir,f"{curdate}")
        #today_dir = os.path.join(src_op_dir,"test")
        # check existence of today_dir, because someday there is 0 cases
        if os.path.exists(today_dir):
            for acc_num in os.listdir(today_dir):
                #the acc_num should be all numbers
                if acc_num.isdigit():
                    acc_dir = os.path.join(today_dir, acc_num)
                    classifydicom(acc_dir,logdate_dir,mod_op)

    time.sleep(120)
