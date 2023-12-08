import arcpy
import csv
import codecs
import os
import sys  
reload(sys)
sys.setdefaultencoding("utf-8")
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [csv2shape]


class csv2shape(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "csv2shape"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        coors_table = arcpy.Parameter(name="coors_table",
                                  displayName="input coords table",
                                  direction="Input",
                                  datatype='DETextfile',
                                  parameterType="Required")

        output_folder = arcpy.Parameter(name="output_folder",
                                  displayName="Output Folder",
                                  direction="Input",
                                  datatype='DEFolder',
                                  parameterType="Required")
        params = [coors_table,output_folder]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        coors_table=parameters[0].valueAsText
        output_folder=parameters[1].valueAsText
        path,temp = os.path.split(coors_table)
        file_name,extension = os.path.splitext(temp)
        ouptname =file_name
        CUR_PATH=os.path.dirname(__file__)
        gdbname=ouptname
        gdbfile = os.path.join(output_folder,gdbname+'.gdb')
        SR= arcpy.Describe(os.path.join(CUR_PATH,'dllib','template.shp')).spatialReference
        arcpy.CreateFileGDB_management(output_folder, gdbname, 'CURRENT')
        arcpy.env.overwriteOutput=True
        arcpy.env.workspace = gdbfile
        tempplate=os.path.join(CUR_PATH,'dllib','template.shp')
        arcpy.CreateFeatureclass_management(gdbfile, ouptname, 'POLYGON',tempplate, 'DISABLED', 'DISABLED', SR)
        fields = arcpy.ListFields(os.path.join(gdbfile,ouptname))
        geometryfield="SHAPE"
        for field in fields:
            if field.type =='Geometry':
                geometryfield=field.name
        frows = arcpy.InsertCursor(os.path.join(gdbfile,ouptname))
        with codecs.open(coors_table,'r',encoding='UTF-8-sig') as f:
            reader=csv.reader(f)
            head_row=next(reader)
            tablediectory={}
            for index,coloum_header in enumerate(head_row):
                tablediectory[coloum_header.lower()] = index
            for row in reader:
                fileddiectory=tablediectory.copy()
                del fileddiectory['ewbj']
                try:
                    frow = frows.newRow()
                    for key,value in fileddiectory.items():
                        frow.setValue(key, str(row[tablediectory[key]]))
                        arcpy.AddMessage('key:%s.' %str(row[tablediectory[key]]))
                        #arcpy.AddMessage('ewbj:%s.' %arcpy.FromWKT(row[tablediectory['ewbj']],SR))
                        frow.setValue(geometryfield, arcpy.FromWKT(row[tablediectory['ewbj']],SR)) 
                    frows.insertRow(frow)
                except:
                    del frow
                else:
                    del frow
        del frows
        return
