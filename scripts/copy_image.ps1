Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$imagePath = "C:\Users\2005g\Downloads\tappits-linkedin-agents\memory\post_images\2026-11-17_tutorial_clones_vs_real_users.png"
$image = [System.Drawing.Image]::FromFile($imagePath)
[System.Windows.Forms.Clipboard]::SetImage($image)
Write-Output "Image copied to clipboard."


