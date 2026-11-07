"""Repair only invalid scene cuts; preserve native master and every rendered PNG."""
from pathlib import Path
import subprocess,json,tempfile,hashlib
R=Path(__file__).resolve().parents[1]; checkpoint=json.loads((R/'reports/github_checkpoint.json').read_text());assert checkpoint['frames_backup_verified'],'Complete durable backup before production changes'
master=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4'; mastersha=hashlib.sha256(master.read_bytes()).hexdigest(); changes=[]
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration','-of','json',str(p)]))['streams'][0]
for i in range(10):
 start=i*8; duration=8 if i<9 else 6; expected=duration*30; path=R/'scenes'/f'SCENE_{i+1:02d}_V3.mp4'
 if path.exists() and int(probe(path)['nb_frames'])==expected:
  print('PRESERVED_VALID_SCENE',i+1,flush=True);continue
 before=probe(path) if path.exists() else None
 with tempfile.TemporaryDirectory(dir=R/'scenes') as tmp:
  video=Path(tmp)/'exact_video.mp4';candidate=Path(tmp)/'scene.mp4'
  # -t alone includes two following video packets because of B-frame DTS reordering.
  subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-ss',str(start),'-i',str(master),'-map','0:v:0','-an','-c:v','copy','-frames:v',str(expected),str(video)],check=True)
  assert int(probe(video)['nb_frames'])==expected
  subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(video),'-ss',str(start),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(duration),'-movflags','+faststart',str(candidate)],check=True)
  after=probe(candidate);assert int(after['nb_frames'])==expected and abs(float(after['duration'])-duration)<.002
  subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(candidate),'-f','null','-'],check=True)
  candidate.replace(path)
 changes.append({'scene':i+1,'before':before,'after':after,'method':'Exact video packet count, then mux original AAC; no rendering or video re-encoding.'});print('SCENE_REPAIRED',i+1,expected,flush=True)
assert hashlib.sha256(master.read_bytes()).hexdigest()==mastersha
(R/'reports/scene_export_repair.json').write_text(json.dumps({'changes':changes,'master_unchanged_sha256':mastersha,'rendered_frames_unchanged':True},indent=2))
