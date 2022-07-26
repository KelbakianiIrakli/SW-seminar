import re
import os
import sys

def extractComments(inputFile, OutputFile, python=False):
    f = open(inputFile, 'r')
    a = f.read()
    pattern = re.compile(r'((.*(\n|\r|\r\n)){1})(((^#.*\n)+)|((\/\/.*\n)+)|(\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+\/[\r\n])|("{3}([^"-]|[\r\n]){1,1000}"{3}[\r\n]))(.*)', re.MULTILINE)
    match = re.finditer(pattern, a)
    f.close()
    for m in match:
        s = m.start()
        e = m.end()
        with open(OutputFile, "a+") as file_object:
            file_object.write(a[s:e])
            file_object.write("\n")
            

def main():
    contributors = {}
    contributor = sys.argv[1]
    contributors[contributor] = []
    for key,value in contributors.items():
        stdout = os.popen("echo \"{0}\" | ~/lookup/getValues A2c".format(key))
        lines = stdout.read().strip().split(";")[1:]
        contributors[key]= lines

    for key, value in contributors.items():
        for c in value:
            with open("processed_commits.txt", "r+") as f:
                 text = f.read()
                 if c in text:
                      continue
                 f.write(c+";")
            stdout = os.popen("echo {0} | ssh da4 ~/lookup/cmputeDiff3T.perl".format(c))
            commitModifications = stdout.read()
            commitModifications= commitModifications.split("\n")
            commitModifications = [x for x in commitModifications if x != '']
            for fileModification in range(len(commitModifications)):
                commitModifications[fileModification] = commitModifications[fileModification].rstrip()
                if (commitModifications[fileModification][-1] == ";"):
                    commitModifications[fileModification] = commitModifications[fileModification][:-1]

            # print(len(res[index]))
                if ".java" in commitModifications[fileModification]:
                    blobInfo = commitModifications[fileModification].split(";")
                    if len(blobInfo) == 3:
                        os.system("echo {0} | ~/lookup/showCnt blob > java_blob_new_file.txt".format(blobInfo[-1]))
                        os.system("sed 's/^ *//g' < java_blob_new_file.txt > java_cleaned_diff_no_whitespace.txt")
                        extractComments("java_cleaned_diff_no_whitespace.txt","java_comments.txt" )
                    else:
                        print(blobInfo[-1], blobInfo[-2])
                        os.system("echo {0} | ~/lookup/showCnt blob > java_blob_before_changes.txt".format(blobInfo[-1].rstrip()))
                        os.system("echo {0} | ~/lookup/showCnt blob > java_blob_after_changes.txt".format(blobInfo[-2].rstrip()))
                        os.system("diff java_blob_before_changes.txt java_blob_after_changes.txt > java_diff_of_blobs.txt")
                        # removes lines with starting < (We do not need to process data which was removed by commit)
                        os.system("sed '/^</ d' < java_diff_of_blobs.txt > java_delete_removed_lines.txt")
                        # removes character > at the start of line
                        os.system("sed 's/^>//' < java_delete_removed_lines.txt > java_cleaned_diff.txt")
                        # removes whitespaces at the beginning of line
                        os.system("sed 's/^ *//g' < java_cleaned_diff.txt > java_cleaned_diff_no_whitespace.txt")
                        extractComments("java_cleaned_diff_no_whitespace.txt", "java_comments.txt")

                elif (".py" in commitModifications[fileModification] or ".ipynb" in commitModifications[fileModification]):
                    blobInfo = commitModifications[fileModification].split(";")
                    if len(blobInfo) == 3:
                        print("blob info size was 3")
                        os.system("echo {0} | ~/lookup/showCnt blob > python_blob_new_file.txt".format(blobInfo[-1]))
                        os.system("sed 's/^ *//g' < python_blob_new_file.txt > python_cleaned_diff_no_whitespace.txt")
                        extractComments("python_cleaned_diff_no_whitespace.txt", "python_comments.txt", True )
                    else:
                        print(blobInfo[-1], blobInfo[-2])
                        os.system("echo {0} | ~/lookup/showCnt blob > python_blob_before_changes.txt".format(blobInfo[-1].rstrip()))
                        os.system("echo {0} | ~/lookup/showCnt blob > python_blob_after_changes.txt".format(blobInfo[-2].rstrip()))
                        
                        os.system("diff python_blob_before_changes.txt python_blob_after_changes.txt > python_diff_of_blobs.txt")
                        # removes lines with starting < (We do not need to process data which was removed by commit)
                        os.system("sed '/^</ d' < python_diff_of_blobs.txt > python_delete_removed_lines.txt")
                        # removes character > at the start of line
                        os.system("sed 's/^>//' < python_delete_removed_lines.txt >> python_cleaned_diff.txt")
                        # removes whitespaces at the beginning of line
                        os.system("sed 's/^ *//g' < python_cleaned_diff.txt > python_cleaned_diff_no_whitespace.txt")
                        extractComments("python_cleaned_diff_no_whitespace.txt", "python_comments.txt", True)

if __name__ == "__main__":
    print("Program is started...")
    main()
        

