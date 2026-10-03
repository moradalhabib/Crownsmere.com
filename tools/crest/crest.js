/*
 * Crownsmere Estate: the 3D gold crest on the home page.
 *
 * The crown-and-CS monogram (traced from the brand logo into crest-shape.json) is
 * extruded and bevelled, finished in polished gold with studio reflections, and
 * lit by a slow light sweep. It tilts towards the pointer (or the phone's
 * orientation), sways gently, and turns away as the hero scrolls out of view.
 * It also places the engraved seal (an SVG ring in the page) around itself, and
 * tilts it with the crest.
 *
 * Build: cd tools/crest && npm install && npm run build
 */
import {
  ACESFilmicToneMapping, BufferAttribute, BufferGeometry, CanvasTexture, Color,
  DirectionalLight, ExtrudeGeometry, Group, MathUtils, Mesh, MeshPhysicalMaterial, NormalBlending, PMREMGenerator,
  PerspectiveCamera, PointLight, Points, PointsMaterial, Scene, Shape, Vector2, Vector3, WebGLRenderer, SRGBColorSpace,
} from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import SHAPES from "./crest-shape.json";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const touch = window.matchMedia("(pointer: coarse)").matches;

function buildShapes() {
  return SHAPES.map((s) => {
    const shape = new Shape(s.o.map(([x, y]) => new Vector2(x, y)));
    s.h.forEach((h) => shape.holes.push(new Shape(h.map(([x, y]) => new Vector2(x, y)))));
    return shape;
  });
}

function dustTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d");
  const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, "rgba(196,158,92,1)");
  grd.addColorStop(0.4, "rgba(176,141,87,0.5)");
  grd.addColorStop(1, "rgba(176,141,87,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 64, 64);
  const t = new CanvasTexture(c);
  t.colorSpace = SRGBColorSpace;
  return t;
}

export function mountCrest(canvas, host) {
  let renderer;
  try {
    renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  } catch (e) {
    return false;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, touch ? 1.5 : 1.75));
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.toneMapping = ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.92;
  renderer.setClearColor(0x000000, 0);

  const scene = new Scene();
  const pmrem = new PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.035).texture;

  const camera = new PerspectiveCamera(28, 1, 0.1, 100);
  camera.position.set(0, 0, 8.4);

  // Gold: physically based, slightly brushed, with a lacquer-like clearcoat
  const gold = new MeshPhysicalMaterial({
    color: new Color("#d4a14f"),
    metalness: 1,
    roughness: 0.27,
    clearcoat: 0.35,
    clearcoatRoughness: 0.18,
    envMapIntensity: 0.8,
  });

  const geo = new ExtrudeGeometry(buildShapes(), {
    depth: 0.14,
    bevelEnabled: true,
    bevelThickness: 0.045,
    bevelSize: 0.022,
    bevelSegments: 5,
    curveSegments: 4,
  });
  geo.center();
  geo.computeBoundingBox();
  const crestH = geo.boundingBox.max.y - geo.boundingBox.min.y;
  const crest = new Mesh(geo, gold);
  const rig = new Group();
  rig.add(crest);
  scene.add(rig);

  // Lights: warm key, soft cream rim, and a moving glint
  const key = new DirectionalLight(0xfff1d6, 1.8);
  key.position.set(3, 4, 6);
  const rim = new DirectionalLight(0xffe2b8, 1.2);
  rim.position.set(-5, -1, -3);
  const glint = new PointLight(0xffd99a, 9, 9, 1.6);
  glint.position.set(-3, 2, 3);
  scene.add(key, rim, glint);

  // Gold dust on cream, drifting very slowly
  const N = touch ? 140 : 260;
  const pos = new Float32Array(N * 3);
  const seed = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 9;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 6;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 4 - 0.5;
    seed[i] = Math.random() * Math.PI * 2;
  }
  const dustGeo = new BufferGeometry();
  dustGeo.setAttribute("position", new BufferAttribute(pos, 3));
  const dust = new Points(dustGeo, new PointsMaterial({
    size: 0.05, map: dustTexture(), transparent: true, opacity: 0.42,
    depthWrite: false, blending: NormalBlending, sizeAttenuation: true,
  }));
  scene.add(dust);

  // Interaction state
  const target = { x: 0, y: 0 };
  const cur = { x: 0, y: 0 };
  let scrollP = 0;
  let visible = true;
  let start = performance.now();
  const seal = host.querySelector(".seal");
  let sealRing = 1.24;
  let sealLast = "";

  const T = Math.tan(MathUtils.degToRad(camera.fov / 2));
  function size() {
    const box = canvas.parentElement;   // the stage: the whole hero, or on phones a space above the text
    const w = box.clientWidth;
    const h = box.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // keep the crest a comfortable size on any screen
    const ratio = w / h;
    if (h < host.clientHeight - 2) {  // phones: fill the space, with the seal just inside it
      sealRing = 1.16;
      const px = (Math.min(w, h) * 0.94) / sealRing;
      camera.position.z = (crestH * h) / (2 * T * px);
      rig.position.y = 0;
    } else if (ratio < 1.05) {     // tablets (portrait) and square windows
      camera.position.z = 10.2;
      rig.position.y = 0.95;
      sealRing = 1.24;
    } else {
      camera.position.z = 8.3;
      rig.position.y = 0.5;
      sealRing = 1.24;
    }
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();
    // centre the engraved seal on the crest, a little larger than it
    if (seal) {
      const c = new Vector3(0, rig.position.y, 0).project(camera);
      const top = new Vector3(0, rig.position.y + (crestH * sealRing) / 2, 0).project(camera);
      const cy = ((1 - c.y) / 2) * h;
      const ty = ((1 - top.y) / 2) * h;
      seal.style.setProperty("--seal-y", cy.toFixed(1) + "px");
      seal.style.setProperty("--seal-d", (2 * (cy - ty)).toFixed(1) + "px");
    }
  }

  function onPointer(e) {
    target.x = (e.clientX / window.innerWidth) * 2 - 1;
    target.y = (e.clientY / window.innerHeight) * 2 - 1;
  }
  function onTilt(e) {
    if (e.gamma == null) return;
    target.x = MathUtils.clamp(e.gamma / 30, -1, 1);
    target.y = MathUtils.clamp((e.beta - 45) / 30, -1, 1);
  }
  function onScroll() {
    const r = host.getBoundingClientRect();
    scrollP = MathUtils.clamp(-r.top / Math.max(1, r.height), 0, 1);
  }

  function frame(now) {
    const t = (now - start) / 1000;
    // entrance: rise and turn into place over ~2.4s
    const intro = reduce ? 1 : MathUtils.smootherstep(t, 0.15, 2.6);
    cur.x += (target.x - cur.x) * 0.05;
    cur.y += (target.y - cur.y) * 0.05;
    const sway = reduce ? 0 : Math.sin(t * 0.32) * 0.22;
    rig.rotation.y = (1 - intro) * -1.1 + sway + cur.x * 0.42 + scrollP * 1.6;
    rig.rotation.x = cur.y * 0.22 + scrollP * 0.25;
    crest.position.y = (1 - intro) * -0.5 + scrollP * 0.9;
    const s = 0.92 + intro * 0.08 - scrollP * 0.12;
    crest.scale.setScalar(s);
    gold.opacity = 1;
    // the glint travels across the crest every ~9 seconds
    const g = reduce ? 0.3 : (t * 0.11) % 1;
    glint.position.set(MathUtils.lerp(-4, 4, g), 2.2 - g * 1.2, 3);
    glint.intensity = 9 * Math.sin(Math.PI * g) + 1.5;
    // the seal leans with the crest, and fades as the hero scrolls away
    if (seal) {
      const v = (-cur.y * 8).toFixed(2) + "," + (cur.x * 12).toFixed(2) + "," + Math.max(0, 1 - scrollP * 2.2).toFixed(2);
      if (v !== sealLast) {
        sealLast = v;
        const [rx, ry, o] = v.split(",");
        seal.style.setProperty("--seal-rx", rx + "deg");
        seal.style.setProperty("--seal-ry", ry + "deg");
        seal.style.opacity = o;
      }
    }
    // dust drift
    if (!reduce) {
      const a = dustGeo.attributes.position.array;
      for (let i = 0; i < N; i++) {
        a[i * 3 + 1] += 0.0016 + Math.sin(t * 0.6 + seed[i]) * 0.0006;
        a[i * 3] += Math.cos(t * 0.4 + seed[i]) * 0.0006;
        if (a[i * 3 + 1] > 3) a[i * 3 + 1] = -3;
      }
      dustGeo.attributes.position.needsUpdate = true;
      dust.rotation.y = cur.x * 0.15;
    }
    renderer.render(scene, camera);
  }

  let raf = 0;
  function loop(now) {
    raf = 0;
    if (!visible || document.hidden) return;
    frame(now);
    if (!reduce) raf = requestAnimationFrame(loop);
  }
  function kick() {
    if (!raf) raf = requestAnimationFrame(loop);
  }

  size();
  window.addEventListener("resize", () => { size(); kick(); });
  window.addEventListener("scroll", () => { onScroll(); kick(); }, { passive: true });
  if (!touch) window.addEventListener("pointermove", onPointer, { passive: true });
  else window.addEventListener("deviceorientation", onTilt, { passive: true });
  document.addEventListener("visibilitychange", kick);
  new IntersectionObserver((en) => { visible = en[0].isIntersecting; kick(); }).observe(host);
  onScroll();
  frame(performance.now());
  kick();
  return true;
}
