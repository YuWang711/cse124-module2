

I'm using python unit test to test my code. The file should be test.py command: python test.py result is in an output file.

List of tests are:

#Basic Functions 200 code response 
  test_Good_Default_Path_Test
  test_Good_Subdirectory_Default_Path
  test_Good_Empty
  test_Jpeg_Image
  test_nested_directory
  test_PNG_Image
  test_Good_Relative_Path
  test_Large_Request
#Basic non-200 error code
  test_File_Not_Found
  test_Malformed_URL
  test_Host_Header_Missing
  test_Error_GETT
  test_Path_Escaping
  test_File_Not_Found_Subdirectory
  test_Malformed_Header_Test
  test_HTTP_Missing
  test_Partial_Request_Timeout
#Concurrency
  test_Concurrency
#Pipeline
  test_Pipeline_Request
  test_Pipeline_with_404_Request
  test_Pipeline_with_400_Request

