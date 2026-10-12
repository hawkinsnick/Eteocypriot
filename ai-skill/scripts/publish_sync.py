"""Publish only a validated bundle on its exact source parent; never rebase or force."""
import argparse,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
def allowed(path):return path.startswith('ai-skill/generated/') or path=='ai-skill/Research-Starter.txt'
def publish(root,expected,before_push=None):
 root=Path(root)
 if not re.fullmatch('[0-9a-f]{40}',expected) or git(root,'rev-parse','HEAD')!=expected:raise ValueError('checkout is not the expected source revision')
 for p in ['ai-skill/generated/research-bundle-index.json','ai-skill/generated/source-state.json']:
  if json.loads((root/p).read_text()).get('source_commit')!=expected:raise ValueError('bundle/source revision mismatch')
 changes=git(root,'diff','--name-only','HEAD').splitlines()+git(root,'ls-files','--others','--exclude-standard').splitlines()
 if any(not allowed(p) for p in changes):raise ValueError('canonical or unrelated changes cannot be published by bundle sync')
 subprocess.run(['python','ai-skill/scripts/validate_bundle.py'],cwd=root,check=True)
 subprocess.run(['git','fetch','--no-tags','origin','main'],cwd=root,check=True,stdout=subprocess.DEVNULL)
 if git(root,'rev-parse','refs/remotes/origin/main')!=expected:
  return {'status':'SKIPPED_SOURCE_ADVANCED','published':False,'source_commit':expected,'reason':'Rebuild from current main; the checked source tree is never rebased.'}
 subprocess.run(['git','add','--','ai-skill/generated'],cwd=root,check=True)
 if (root/'ai-skill/Research-Starter.txt').exists():subprocess.run(['git','add','--','ai-skill/Research-Starter.txt'],cwd=root,check=True)
 staged=git(root,'diff','--cached','--name-only').splitlines()
 if any(not allowed(p) for p in staged):raise ValueError('unrelated staged change')
 if not staged:return {'status':'NO_GENERATED_CHANGES','published':False,'source_commit':expected}
 subprocess.run(['git','commit','-m','chore(ai-skill): sync validated bundle to corpus '+expected[:12]],cwd=root,check=True,stdout=subprocess.DEVNULL)
 head=git(root,'rev-parse','HEAD')
 if git(root,'rev-parse','HEAD^')!=expected:raise ValueError('generated commit does not descend directly from checked source')
 if before_push:before_push()
 # Atomic Git fast-forward check rejects a racing writer. No pull/rebase/force fallback.
 subprocess.run(['git','push','origin','HEAD:refs/heads/main'],cwd=root,check=True,stdout=subprocess.DEVNULL)
 return {'status':'PUBLISHED_EXACT_SOURCE_PARENT','published':True,'source_commit':expected,'bundle_commit':head}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',default=os.environ.get('SOURCE_COMMIT') or os.environ.get('GITHUB_SHA'));a=p.parse_args();print(json.dumps(publish(ROOT,a.source)))
