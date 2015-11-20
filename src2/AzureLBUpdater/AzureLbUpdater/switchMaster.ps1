
param (
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [ValidateSet('0', '1')]
    [String]$NewMaster
)


$newVmMaster = ''
$oldVmMaster = ''

if ($NewMaster -eq '1'){
	$newVmMaster = 'BackendVM1'
	$oldVmMaster = 'BackendVM0'
}
else {
	$newVmMaster = 'BackendVM0'
	$oldVmMaster = 'BackendVM1'
}

$arguments = $newVmMaster + ' ' + $oldVmMaster

Start-Process -FilePath './AzureLbUpdater.exe' -ArgumentList $arguments -NoNewWindow


Write-Host -ForegroundColor Yellow -Object 'Done with processing...'



