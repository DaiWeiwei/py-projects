# coding=utf-8
import robot

robot.run(r"E:\umac_project_version_valid\code\testcases\umac.tsv",
          test=u"upgrade_ind_board",
          #test = u"upgrade_umac",
          #listener=r"C:\Python27\lib\site-packages\robotide\contrib\testrunner\TestRunnerAgent.py:60757:False",
          loglevel="TRACE")
