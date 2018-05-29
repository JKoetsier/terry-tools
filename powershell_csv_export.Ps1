$server = "WIN-N7N4MEN8F6G"
$database = "AccBiqh"
$tablequery = "SELECT name from sys.tables"
$directory = "C:\Users\Administrator\Documents\flatfile_export"

#Delcare Connection Variables
$connectionTemplate = "Data Source={0};Integrated Security=SSPI;Initial Catalog={1};"
$connectionString = [string]::Format($connectionTemplate, $server, $database)
$connection = New-Object System.Data.SqlClient.SqlConnection
$connection.ConnectionString = $connectionString

$command = New-Object System.Data.SqlClient.SqlCommand
$command.CommandText = $tablequery
$command.Connection = $connection

#Load up the Tables in a dataset
$SqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter
$SqlAdapter.SelectCommand = $command
$DataSet = New-Object System.Data.DataSet
$SqlAdapter.Fill($DataSet)
$connection.Close()

$tmpdir = $directory + "\tmp"

# Create tmp dir
if (!(Test-Path $tmpDir)) {
    New-Item -ItemType directory -Path $tmpdir
}

# Empty tmp dir
Get-ChildItem -Path $tmpdir -Include * -File -Recurse | foreach { $_.Delete()}

# Loop through all tables and export a CSV of the Table Data
foreach ($Row in $DataSet.Tables[0].Rows)
{

    #Specify the output location of your dump file
    $filename = $($Row[0]) + ".csv"
    $extractFile = $directory + "\" + $filename
    $tmpFile = $tmpdir + "\" + $filename

    if (!(Test-Path $extractFile -PathType Leaf)) {
        Write-Host $extractFile
        $queryData = "SELECT * FROM [$($Row[0])]"
        $command.CommandText = $queryData
        $command.Connection = $connection

        $SqlAdapter = New-Object System.Data.SqlClient.SqlDataAdapter
        $SqlAdapter.SelectCommand = $command
        $DataSet = New-Object System.Data.DataSet
        $SqlAdapter.Fill($DataSet)
        $connection.Close()

        $DataSet.Tables[0]  | Export-Csv $tmpFile -NoTypeInformation
        Move-Item $tmpFile $extractFile

    }
}
