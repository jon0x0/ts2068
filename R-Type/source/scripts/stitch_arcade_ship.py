from pathlib import Path
import cv2,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
 folder=ROOT/'build/fullgame/arcade_reference';sift=cv2.SIFT_create();views=[];positions=[];previous=None;offset=np.zeros(2);report=[]
 for frame in range(21000,28201,300):
  rgb=np.asarray(Image.open(folder/f'frame{frame:06d}.png').convert('RGB'));a=rgb.astype(int);green=((a[:,:,1]>a[:,:,0]+7)&(a[:,:,1]>a[:,:,2]+7)).astype('uint8')*255;green[:32]=0;green[216:]=0
  k,desc=sift.detectAndCompute(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),green)
  if desc is None or len(k)<12:continue
  if previous is not None:
   pk,pd=previous;matches=cv2.BFMatcher().knnMatch(pd,desc,k=2);good=[p for p,q in matches if p.distance<.7*q.distance];vectors=np.array([np.array(pk[p.queryIdx].pt)-np.array(k[p.trainIdx].pt)for p in good])
   if len(vectors)<6:continue
   bins=np.round(vectors/2).astype(int);keys,counts=np.unique(bins,axis=0,return_counts=True);peak=keys[np.argmax(counts)]*2;inside=np.linalg.norm(vectors-peak,axis=1)<4
   if inside.sum()<6:continue
   delta=np.median(vectors[inside],axis=0);offset=offset+delta;report.append(dict(frame=frame,dx=float(delta[0]),dy=float(delta[1]),inliers=int(inside.sum())))
  mask=cv2.dilate(green,np.ones((23,23),dtype='uint8'));mask[:32]=0;mask[216:]=0;mask[(rgb.max(2)<12)]=0
  rgba=np.concatenate([rgb,mask[:,:,None]],axis=2);views.append(Image.fromarray(rgba,'RGBA'));positions.append(offset.copy());previous=(k,desc)
 assert len(views)>=4,(len(views),report)
 positions=np.round(positions).astype(int);low=positions.min(0);high=positions.max(0)+[384,256];canvas=Image.new('RGBA',tuple(high-low))
 for image,p in zip(views,positions):canvas.alpha_composite(image,tuple(p-low))
 bbox=canvas.getbbox();canvas=canvas.crop(bbox);out=ROOT/'build/fullgame/arcade_objects';canvas.save(out/'giant_ship_panorama.png');(out/'giant_ship_stitch.json').write_text(json.dumps(dict(views=len(views),size=canvas.size,translations=report,method='SIFT matches constrained to green arcade hull pixels; robust translation consensus; source screenshots unmodified'),indent=2));print('Panorama',canvas.size,report)
if __name__=='__main__':main()
