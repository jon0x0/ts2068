"""Prepare a real ray-traced grayscale still for the native one-bit display."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent

def unit(v):
    return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-12)

def intersect(origin,direction):
    shape=direction.shape[:-1]
    best=np.full(shape,np.inf);normal=np.zeros_like(direction);material=np.zeros(shape,dtype=np.int8)
    def accept(t,n,mid):
        nonlocal best,normal,material
        use=(t>1e-4)&(t<best)
        best=np.where(use,t,best);normal=np.where(use[...,None],n,normal);material=np.where(use,mid,material)
    # Large satin sphere and a smaller polished sphere.
    for center,radius,mid in [((-1.25,.82,.05),.82,1),((.12,.34,.88),.34,2)]:
        delta=origin-np.array(center)
        b=np.sum(delta*direction,axis=-1);c=np.sum(delta*delta,axis=-1)-radius**2
        disc=b*b-c;t=np.where(disc>=0,-b-np.sqrt(np.maximum(disc,0)),np.inf)
        point=origin+np.where(np.isfinite(t),t,0)[...,None]*direction
        accept(t,unit(point-np.array(center)),mid)
    # Box with three distinctly illuminated faces.
    lo=np.array((.65,0,-.65));hi=np.array((1.85,1.3,.55))
    safe=np.where(np.abs(direction)>1e-12,direction,1e-12)
    a=(lo-origin)/safe;b=(hi-origin)/safe
    near=np.minimum(a,b);far=np.maximum(a,b)
    entry=np.max(near,axis=-1);leave=np.min(far,axis=-1)
    axis=np.argmax(near,axis=-1)
    n=np.zeros_like(direction)
    for j in range(3):n[...,j]=np.where(axis==j,-np.sign(direction[...,j]),0)
    accept(np.where(leave>=entry,entry,np.inf),n,3)
    # Horizontal ground plane.
    dy=direction[...,1]
    t=np.where(np.abs(dy)>1e-12,-origin[...,1]/np.where(np.abs(dy)>1e-12,dy,1),np.inf)
    n=np.zeros_like(direction);n[...,1]=1
    accept(t,n,4)
    return best,normal,material

def render_scene():
    w,h=1024,336
    camera=np.array((3.8,2.7,6.0));target=np.array((0,.65,.1))
    forward=unit(target-camera);right=unit(np.cross(forward,np.array((0,1,0))))
    up=unit(np.cross(right,forward))
    yy,xx=np.mgrid[0:h,0:w]
    scale=np.tan(np.deg2rad(29)/2)
    sx=((xx+.5)/w*2-1)*(w/h)*scale;sy=(1-(yy+.5)/h*2)*scale
    direction=unit(forward+sx[...,None]*right+sy[...,None]*up)
    distance,normal,material=intersect(camera,direction)
    hit=material!=0;point=camera+np.where(hit,distance,0)[...,None]*direction
    # Neutral floor with subtle world-space checks supplies perspective cues.
    checks=(np.floor(point[...,0]*1.15)+np.floor(point[...,2]*1.15)).astype(int)&1
    albedo=np.where(material==4,np.where(checks,.42,.57),np.where(material==3,.65,.76))
    diffuse=np.zeros((h,w));specular=np.zeros((h,w))
    for dx,dz in [(-.25,-.25),(-.25,.25),(.25,-.25),(.25,.25)]:
        light=np.array((-3.0+dx,5.5,3.8+dz))
        tolight=light-point;lightdistance=np.linalg.norm(tolight,axis=-1)
        l=unit(tolight);shadowdist,_,_=intersect(point+normal*.002,l)
        visible=shadowdist>lightdistance
        diffuse+=np.maximum(np.sum(normal*l,axis=-1),0)*visible/4
        half=unit(l-direction)
        exponent=np.where(material==2,100,38)
        specular+=np.maximum(np.sum(normal*half,axis=-1),0)**exponent*visible/4
    shade=albedo*(.16+.78*diffuse)+.40*specular
    # Soft contact darkening is static shading, not a screen-space overlay.
    contact=np.minimum(1,.65+point[...,1]*.4)
    shade=np.where(material==4,shade,shade*contact)
    fog=np.exp(-np.maximum(distance-8,0)*.10)
    shade=shade*fog+.10*(1-fog)
    sky=.09+.04*(1-yy/h)
    shade=np.where(hit,shade,sky)
    image=Image.fromarray(np.uint8(np.clip(shade,0,1)**(1/1.7)*255))
    # Correct physical aspect: the high-res hardware pixels are narrow.
    image=image.resize((512,168),Image.Resampling.LANCZOS)
    image.save(ROOT/'scene-grayscale.png')
    native=image.resize((512,84),Image.Resampling.LANCZOS)
    native=native.convert('1',dither=Image.Dither.FLOYDSTEINBERG)
    native.save(ROOT/'scene-dithered-512x84.png')
    return native

if __name__=='__main__':render_scene()
