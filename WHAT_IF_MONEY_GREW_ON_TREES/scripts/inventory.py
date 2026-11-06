from pathlib import Path
import sys,os,shutil,subprocess,json,platform,importlib.metadata
R=Path(__file__).resolve().parents[1]
names=['blender','python','python3','ffmpeg','ffprobe','espeak','espeak-ng','piper','festival','flite','sox','aplay','timidity','fluidsynth','nvidia-smi']
binaries={n:shutil.which(n) for n in names}
path_bins=sorted({p.name for d in os.get_exec_path() if Path(d).is_dir() for p in Path(d).iterdir() if p.is_file() and os.access(p,os.X_OK)})
result={'python':sys.version,'platform':platform.platform(),'cpus':os.cpu_count(),'binaries':binaries,'accessible_binary_names':path_bins,'python_packages':sorted([{'name':d.metadata['Name'],'version':d.version} for d in importlib.metadata.distributions()],key=lambda x:x['name'].lower()),'skills':['cloud-environment:cloud-environment-runtime (already loaded)','cloud-environment-onboarding:setup (already loaded)'],'executor_skills':[],'installations_performed':[],'audio_choice':'Existing FFmpeg flite / CMU slt voice. No installation needed.','reference_access':'403 CONNECT denial; reference not viewed; written brief used.'}
(R/'reports'/'environment_inventory.json').write_text(json.dumps(result,indent=2))
print('Inventoried',len(path_bins),'accessible binary names and',len(result['python_packages']),'Python packages. No installation.')
