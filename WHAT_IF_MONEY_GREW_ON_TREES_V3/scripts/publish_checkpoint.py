from pathlib import Path
import json,hashlib,sys
from github_io import ROOT as R,ensure_branch,upload,BRANCH
B=R/'recovery'; prefix='recovery/v3-restored-checkpoint';ensure_branch();log=R/'reports/github_checkpoint.json'
old=json.loads(log.read_text()) if log.exists() else {'branch':BRANCH,'artifacts':[]};results={x['path']:x for x in old['artifacts']}
files=[B/'V3_RECOVERY_SOURCE.zip',B/'V3_RECOVERY_BLENDER.zip']
if '--frames' in sys.argv:files=[B/'V3_NATIVE_FRAMES_LOSSLESS.mkv',R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4']
index=[]
for p in files:
 if not p.exists():raise RuntimeError('Missing recovery file: '+p.name)
 entries=[];whole=hashlib.sha256(p.read_bytes()).hexdigest()
 with p.open('rb') as f:
  i=0
  while True:
   block=f.read(19*1024*1024)
   if not block:break
   i+=1;part=B/(p.name+f'.part{i:03d}');part.write_bytes(block);target=prefix+'/'+part.name
   record=upload(part,target);results[target]=record;entries.append(record)
   log.write_text(json.dumps({'branch':BRANCH,'artifacts':list(results.values())},indent=2))
 index.append({'file':p.name,'bytes':p.stat().st_size,'sha256':whole,'parts':entries})
manifest=B/('FRAME_BACKUP_INDEX.json' if '--frames' in sys.argv else 'SOURCE_BACKUP_INDEX.json');manifest.write_text(json.dumps({'files':index,'restore':'Download parts in numerical order, concatenate to recover the named file, verify its whole SHA-256. The lossless frame archive restores the exact RGB pixel hashes in recovery_checkpoint.json using scripts/restore_frames.py. Opaque alpha restored to 255. PNG compressed bytes can differ.'},indent=2));record=upload(manifest,prefix+'/'+manifest.name);results[record['path']]=record
log.write_text(json.dumps({'branch':BRANCH,'artifacts':list(results.values()),'source_backup_verified':True,'frames_backup_verified':'--frames' in sys.argv},indent=2));print('GITHUB_CHECKPOINT_VERIFIED',flush=True)
