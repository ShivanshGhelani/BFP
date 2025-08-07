// SystemProfile: Gathers device/browser info and sends to backend
class SystemProfile {
    constructor() {
        this.info = {};
        this.start = Date.now();
        this.info.visitor_id = this.getOrCreateVisitorId();
        this.info.visit_count = this.getVisitCount();
        // Use improved device detection for mobile/desktop
        this.setDeviceInfo();
    }

    async gatherAll() {
        console.log('[SystemProfile] gatherAll called');
        try {
            await this.setDeviceInfo();
            console.log('[SystemProfile] device info:', this.info.device_brand, this.info.device_model, this.info.os, this.info.osVersion, this.info.deviceType, this.info.architecture);
            this.info.adblock = await this.detectAdBlocker();
            await Promise.all([
                this.gatherNavigator(),
                this.gatherHardware(),
                this.gatherDisplay(),
                this.gatherTimezone(),
                this.gatherCanvas(),
                this.gatherWebGL(),
                this.gatherWebGLFingerprint(),
                this.gatherAudio(),
                this.gatherFonts(),
                this.gatherFeatures(),
                this.gatherNetwork(),
                this.gatherStorage(),
                this.gatherSession(),
                this.gatherCSS(),
                this.gatherLocation(),
                this.gatherMediaDevices(),
                this.gatherSpeechVoices(),
                this.gatherClipboardSupport(),
                this.gatherPermissions(),
                this.gatherBattery()
            ]);
            this.info.collectedAt = Date.now();
            this.info.sessionKey = this.makeSessionKey();
            this.info.collectDuration = Date.now() - this.start;
            console.log('[SystemProfile] gatherAll completed, calling sendToServer');
            await this.sendToServer();
        } catch (e) {
            console.error('[SystemProfile] gatherAll error', e);
        }
    }

    async gatherNavigator() {
        const nav = navigator;
        // Enhanced browser name/version detection with iOS support
        let browserName = 'Unknown', browserVersion = 'Unknown';
        const ua = nav.userAgent;
        
        // iOS-specific browser detection (all use WebKit but have different UAs)
        if (/iphone|ipad|ipod/i.test(ua)) {
            if (/crios/i.test(ua)) {
                browserName = 'Chrome iOS';
                browserVersion = (ua.match(/crios\/([0-9.]+)/i) || [])[1] || 'Unknown';
            } else if (/fxios/i.test(ua)) {
                browserName = 'Firefox iOS';
                browserVersion = (ua.match(/fxios\/([0-9.]+)/i) || [])[1] || 'Unknown';
            } else if (/edgios/i.test(ua)) {
                browserName = 'Edge iOS';
                browserVersion = (ua.match(/edgios\/([0-9.]+)/i) || [])[1] || 'Unknown';
            } else if (/opios/i.test(ua)) {
                browserName = 'Opera iOS';
                browserVersion = (ua.match(/opios\/([0-9.]+)/i) || [])[1] || 'Unknown';
            } else if (/safari/i.test(ua) || /mobile\/[0-9a-z]+$/i.test(ua)) {
                browserName = 'Safari iOS';
                browserVersion = (ua.match(/version\/([0-9.]+)/i) || [])[1] || 'Unknown';
            }
        }
        // Desktop/Android browser detection
        else if (/chrome|crios|crmo/i.test(ua) && !/edg/i.test(ua)) {
            browserName = 'Chrome';
            browserVersion = (ua.match(/chrome\/([0-9.]+)/i) || [])[1] || 'Unknown';
        } else if (/firefox|fxios/i.test(ua)) {
            browserName = 'Firefox';
            browserVersion = (ua.match(/firefox\/([0-9.]+)/i) || [])[1] || 'Unknown';
        } else if (/safari/i.test(ua) && !/chrome|crios|crmo/i.test(ua) && !/edg/i.test(ua)) {
            browserName = 'Safari';
            browserVersion = (ua.match(/version\/([0-9.]+)/i) || [])[1] || 'Unknown';
        } else if (/edg/i.test(ua)) {
            browserName = 'Edge';
            browserVersion = (ua.match(/edg\/([0-9.]+)/i) || [])[1] || 'Unknown';
        } else if (/opera|opr/i.test(ua)) {
            browserName = 'Opera';
            browserVersion = (ua.match(/(opera|opr)\/([0-9.]+)/i) || [])[2] || 'Unknown';
        }
        // Try to use UA-CH if available
        if (nav.userAgentData && nav.userAgentData.brands) {
            const brands = nav.userAgentData.brands;
            const mainBrand = brands.find(b => b.brand !== 'Not?A_Brand');
            if (mainBrand) {
                browserName = mainBrand.brand;
                browserVersion = mainBrand.version;
            }
        }
        this.info.navigator = {
            ua: nav.userAgent || '',
            plat: nav.platform || '',
            lang: nav.language || '',
            langs: nav.languages ? [...nav.languages] : [],
            cookies: nav.cookieEnabled,
            online: nav.onLine,
            dnt: nav.doNotTrack,
            java: (typeof nav.javaEnabled === 'function') ? nav.javaEnabled() : false,
            browserName,
            browserVersion
        };
    }
    async gatherHardware() {
        this.info.hardware = {
            cores: navigator.hardwareConcurrency || 'unknown',
            mem: navigator.deviceMemory || 'unknown',
            touch: navigator.maxTouchPoints || 0,
            touchable: 'ontouchstart' in window,
            vibrate: !!navigator.vibrate
        };
    }
    async gatherDisplay() {
        const s = window.screen;
        this.info.display = {
            w: s.width,
            h: s.height,
            res: `${s.width}x${s.height}`,
            aw: s.availWidth,
            ah: s.availHeight,
            cdepth: s.colorDepth,
            pdepth: s.pixelDepth,
            winW: window.innerWidth,
            winH: window.innerHeight,
            outW: window.outerWidth,
            outH: window.outerHeight,
            dpr: window.devicePixelRatio || 1,
            orient: s.orientation ? s.orientation.type : 'unknown'
        };
    }
    async gatherTimezone() {
        this.info.tz = {
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
            offset: new Date().getTimezoneOffset(),
            locale: Intl.DateTimeFormat().resolvedOptions().locale
        };
    }
    async gatherCanvas() {
        try {
            const c = document.createElement('canvas');
            const ctx = c.getContext('2d');
            ctx.textBaseline = 'alphabetic';
            ctx.font = '16px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Browser FP Test', 2, 15);
            ctx.strokeStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.strokeRect(5, 5, 50, 50);
            // More drawing operations for entropy
            ctx.globalAlpha = 0.7;
            ctx.arc(50, 50, 20, 0, Math.PI * 2, true);
            ctx.fillStyle = 'rgba(200, 0, 0, 0.5)';
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(10, 10);
            ctx.lineTo(60, 60);
            ctx.lineTo(10, 60);
            ctx.closePath();
            ctx.stroke();
            ctx.globalAlpha = 1.0;
            // Try different blend modes
            ctx.globalCompositeOperation = 'multiply';
            ctx.fillStyle = 'rgb(0,200,0)';
            ctx.fillRect(30, 30, 40, 40);
            ctx.globalCompositeOperation = 'source-over';
            // Draw with different fonts and rotations
            ctx.save();
            ctx.font = '20px Times New Roman';
            ctx.rotate(0.1);
            ctx.fillStyle = '#0af';
            ctx.fillText('Entropy!', 80, 40);
            ctx.restore();
            ctx.save();
            ctx.font = '18px Courier New';
            ctx.rotate(-0.1);
            ctx.fillStyle = '#fa0';
            ctx.fillText('Canvas FP', 10, 80);
            ctx.restore();
            // Get data
            const dataURL = c.toDataURL();
            this.info.canvas = {
                hash: this.hash(dataURL),
                dataURLLength: dataURL.length
            };
        } catch (e) {
            this.info.canvas = { error: 'no_canvas' };
        }
    }
    async gatherWebGL() {
        try {
            const c = document.createElement('canvas');
            const gl = c.getContext('webgl') || c.getContext('experimental-webgl');
            if (gl) {
                this.info.webgl = {
                    vendor: gl.getParameter(gl.VENDOR),
                    renderer: gl.getParameter(gl.RENDERER),
                    version: gl.getParameter(gl.VERSION),
                    maxTex: gl.getParameter(gl.MAX_TEXTURE_SIZE)
                };
                const dbg = gl.getExtension('WEBGL_debug_renderer_info');
                if (dbg) {
                    this.info.webgl.unmaskedVendor = gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL);
                    this.info.webgl.unmaskedRenderer = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
                }
                // GPU info
                this.info.gpu = {
                    vendor: this.info.webgl.unmaskedVendor || this.info.webgl.vendor,
                    renderer: this.info.webgl.unmaskedRenderer || this.info.webgl.renderer
                };
            } else {
                this.info.webgl = { error: 'no_webgl' };
            }
        } catch (e) {
            this.info.webgl = { error: 'webgl_fail' };
        }
    }
    async gatherWebGLFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 32;
            canvas.height = 32;
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) {
                this.info.webgl_fingerprint = { error: 'no_webgl' };
                return;
            }
            // Simple WebGL scene: clear, draw a colored triangle
            gl.clearColor(0.5, 0.8, 0.1, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            // Vertex shader
            const vsSource = `attribute vec2 pos; void main() { gl_Position = vec4(pos, 0, 1); }`;
            const fsSource = `void main() { gl_FragColor = vec4(0.2, 0.6, 0.9, 1.0); }`;
            function compileShader(type, source) {
                const shader = gl.createShader(type);
                gl.shaderSource(shader, source);
                gl.compileShader(shader);
                return shader;
            }
            const vs = compileShader(gl.VERTEX_SHADER, vsSource);
            const fs = compileShader(gl.FRAGMENT_SHADER, fsSource);
            const program = gl.createProgram();
            gl.attachShader(program, vs);
            gl.attachShader(program, fs);
            gl.linkProgram(program);
            gl.useProgram(program);
            // Triangle vertices
            const vertices = new Float32Array([
                0, 1,  -1, -1,  1, -1
            ]);
            const buf = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, buf);
            gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
            const posLoc = gl.getAttribLocation(program, 'pos');
            gl.enableVertexAttribArray(posLoc);
            gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
            gl.drawArrays(gl.TRIANGLES, 0, 3);
            // Read pixels and hash
            const pixels = new Uint8Array(32 * 32 * 4);
            gl.readPixels(0, 0, 32, 32, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
            let hash = 0;
            for (let i = 0; i < pixels.length; i++) {
                hash = ((hash << 5) - hash) + pixels[i];
                hash |= 0;
            }
            this.info.webgl_fingerprint = { hash: hash.toString() };
        } catch (e) {
            this.info.webgl_fingerprint = { error: 'fail' };
        }
    }
    async gatherAudio() {
        try {
            const AC = window.AudioContext || window.webkitAudioContext;
            if (AC) {
                const ctx = new AC();
                this.info.audio = {
                    rate: ctx.sampleRate,
                    maxCh: ctx.destination.maxChannelCount,
                    state: ctx.state
                };
                ctx.close();
            } else {
                this.info.audio = { error: 'no_audio' };
            }
        } catch (e) {
            this.info.audio = { error: 'audio_fail' };
        }
    }
    async gatherFonts() {
        const fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia'];
        const found = [];
        const c = document.createElement('canvas');
        const ctx = c.getContext('2d');
        const testStr = 'FontTest';
        ctx.font = '72px monospace';
        const baseW = ctx.measureText(testStr).width;
        for (const f of fonts) {
            ctx.font = `72px "${f}", monospace`;
            const w = ctx.measureText(testStr).width;
            if (Math.abs(w - baseW) > 1) found.push(f);
        }
        this.info.fonts = { found, total: fonts.length };
    }
    async gatherFeatures() {
        this.info.features = {
            localStorage: !!window.localStorage,
            sessionStorage: !!window.sessionStorage,
            indexedDB: !!window.indexedDB,
            worker: !!window.Worker,
            sw: !!navigator.serviceWorker,
            ws: !!window.WebSocket,
            rtc: !!(window.RTCPeerConnection || window.webkitRTCPeerConnection),
            geo: !!navigator.geolocation,
            crypto: !!window.crypto,
            notif: !!window.Notification,
            vibrate: !!navigator.vibrate,
            bt: !!navigator.bluetooth,
            usb: !!navigator.usb,
            wasm: !!window.WebAssembly,
            serviceWorkerRegistered: (navigator.serviceWorker && navigator.serviceWorker.controller) ? true : false
        };
        // Notification permission state (detailed)
        if (window.Notification && Notification.permission) {
            this.info.features.notificationPermission = Notification.permission;
        }
        // PWA install status (if applicable)
        this.info.features.isPWA = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    }
    async gatherNetwork() {
        const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        this.info.network = {
            online: navigator.onLine,
            conn: conn ? {
                type: conn.effectiveType,
                down: conn.downlink,
                rtt: conn.rtt,
                save: conn.saveData
            } : null
        };
    }
    async gatherStorage() {
        // Gather localStorage and sessionStorage support
        this.info.storage = {
            local: this.testStorage('localStorage'),
            session: this.testStorage('sessionStorage'),
            cookies: navigator.cookieEnabled
        };
        // Gather all localStorage key-value pairs
        try {
            const localData = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                localData[key] = localStorage.getItem(key);
            }
            this.info.localStorageData = localData;
        } catch (e) {
            this.info.localStorageData = { error: 'not_accessible' };
        }
        // Gather all sessionStorage key-value pairs
        try {
            const sessionData = {};
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                sessionData[key] = sessionStorage.getItem(key);
            }
            this.info.sessionStorageData = sessionData;
        } catch (e) {
            this.info.sessionStorageData = { error: 'not_accessible' };
        }
    }
    testStorage(type) {
        try {
            const s = window[type];
            const k = '__tst__';
            s.setItem(k, 't');
            s.removeItem(k);
            return true;
        } catch (e) {
            return false;
        }
    }
    async gatherSession() {
        this.info.session = {
            ref: document.referrer || '',
            url: window.location.href,
            proto: window.location.protocol,
            host: window.location.host,
            hist: window.history.length,
            pageVisibility: document.visibilityState
        };
    }
    async gatherCSS() {
        this.info.css = {
            dark: window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)').matches : false,
            reduced: window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false,
            fontSize: window.getComputedStyle(document.body).fontSize,
            zoom: window.visualViewport ? window.visualViewport.scale : 1,
            highContrast: window.matchMedia('(forced-colors: active)').matches
        };
    }
    async gatherLocation() {
        this.info.loc = {
            tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
            offset: new Date().getTimezoneOffset()
        };
        // Optionally, fetch IP-based info from backend
        try {
            const resp = await fetch('/api/v1/analytics/ip-info', { method: 'GET', credentials: 'same-origin' });
            if (resp.ok) {
                const result = await resp.json();
                this.info.loc.ipInfo = result.data || result;
            }
        } catch (e) {}
        // Prompt for browser geolocation
        if (navigator.geolocation) {
            try {
                await new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            this.info.loc.gps = {
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                accuracy: position.coords.accuracy
                            };
                            resolve();
                        },
                        (error) => {
                            // User denied or error
                            resolve();
                        },
                        { enableHighAccuracy: false, timeout: 5000, maximumAge: 600000 }
                    );
                });
            } catch (e) {}
        }
    }
    makeSessionKey() {
        return 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now().toString(36);
    }
    hash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash;
    }
    async sendToServer() {
        try {
            console.log('[SystemProfile] sendToServer called', this.info);
            await fetch('/api/v1/analytics/visitor-log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.info),
                credentials: 'same-origin'
            });
        } catch (e) {}
    }
    async getLocalIPs() {
        return new Promise((resolve) => {
            const ips = [];
            const RTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection;
            if (!RTCPeerConnection) {
                resolve([]);
                return;
            }
            const pc = new RTCPeerConnection({iceServers: []});
            pc.createDataChannel("");
            pc.onicecandidate = (event) => {
                if (event && event.candidate && event.candidate.candidate) {
                    const ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
                    const match = ipRegex.exec(event.candidate.candidate);
                    if (match) {
                        if (!ips.includes(match[1]) && !match[1].startsWith("127.")) {
                            ips.push(match[1]);
                        }
                    }
                } else {
                    // ICE gathering finished
                    pc.close();
                    resolve(ips);
                }
            };
            pc.createOffer().then(offer => pc.setLocalDescription(offer));
            // Fallback: resolve after 2 seconds if nothing found
            setTimeout(() => {
                pc.close();
                resolve(ips);
            }, 2000);
        });
    }
    getOrCreateVisitorId() {
        let id = getCookie('visitor_id');
        if (!id) {
            id = 'v_' + Math.random().toString(36).substr(2, 12) + '_' + Date.now().toString(36);
            setCookie('visitor_id', id);
            setCookie('visit_count', 1);
        } else {
            // Increment visit count
            let count = parseInt(getCookie('visit_count') || '0', 10) + 1;
            setCookie('visit_count', count);
        }
        return id;
    }
    getVisitCount() {
        return parseInt(getCookie('visit_count') || '1', 10);
    }
    async detectAdBlocker() {
        return new Promise((resolve) => {
            const test = document.createElement('div');
            test.innerHTML = '&nbsp;';
            test.className = 'adsbox';
            test.style.position = 'absolute';
            test.style.height = '10px';
            document.body.appendChild(test);
            setTimeout(function() {
                resolve(test.offsetHeight === 0);
                test.remove();
            }, 100);
        });
    }
    async gatherMediaDevices() {
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                this.info.mediaDevices = devices.map(d => ({ kind: d.kind, label: d.label, groupId: d.groupId, deviceId: d.deviceId }));
            } catch (e) {
                this.info.mediaDevices = { error: 'not_allowed' };
            }
        } else {
            this.info.mediaDevices = { error: 'not_supported' };
        }
    }
    async gatherSpeechVoices() {
        if (window.speechSynthesis && window.speechSynthesis.getVoices) {
            try {
                const voices = window.speechSynthesis.getVoices();
                this.info.speechVoices = voices.map(v => ({ name: v.name, lang: v.lang, localService: v.localService, default: v.default }));
            } catch (e) {
                this.info.speechVoices = { error: 'not_allowed' };
            }
        } else {
            this.info.speechVoices = { error: 'not_supported' };
        }
    }
    async gatherClipboardSupport() {
        this.info.clipboard = {
            supported: !!navigator.clipboard
        };
    }
    async gatherPermissions() {
        if (navigator.permissions && navigator.permissions.query) {
            try {
                const geo = await navigator.permissions.query({ name: 'geolocation' });
                const notif = await navigator.permissions.query({ name: 'notifications' });
                this.info.permissions = {
                    geolocation: geo.state,
                    notifications: notif.state
                };
            } catch (e) {
                this.info.permissions = { error: 'not_allowed' };
            }
        } else {
            this.info.permissions = { error: 'not_supported' };
        }
    }
    async gatherBattery() {
        // Check if we're on iOS - Battery API is not supported on iOS/Safari
        const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
        
        if (isIOS) {
            this.info.battery = { 
                error: 'ios_not_supported',
                reason: 'Battery API is not available on iOS devices for privacy reasons',
                percentage: null,
                capacity: null
            };
            return;
        }
        
        if (navigator.getBattery) {
            try {
                const battery = await navigator.getBattery();
                this.info.battery = {
                    charging: battery.charging,
                    level: battery.level,
                    percentage: Math.round(battery.level * 100), // Convert 0.0-1.0 to 0-100
                    chargingTime: battery.chargingTime,
                    dischargingTime: battery.dischargingTime,
                    capacity: this.getBatteryCapacity() // Try to get battery capacity
                };
            } catch (e) {
                this.info.battery = { 
                    error: 'not_allowed', 
                    details: e.message,
                    percentage: null,
                    capacity: null
                };
            }
        } else {
            this.info.battery = { 
                error: 'not_supported', 
                reason: 'Battery API not available in this browser',
                percentage: null,
                capacity: null
            };
        }
    }
    
    getBatteryCapacity() {
        // Battery capacity is not directly available through web APIs for security/privacy reasons
        // We can only estimate based on device model for known devices
        try {
            const ua = navigator.userAgent.toLowerCase();
            const platform = navigator.platform || '';
            
            // Try to estimate capacity based on known device patterns
            if (/macbook/i.test(ua) || /macintosh/i.test(ua)) {
                if (/m1|m2|m3/i.test(ua)) return 'Estimated: 50-100Wh (Apple Silicon)';
                return 'Estimated: 50-95Wh (Intel MacBook)';
            }
            
            // For Windows laptops, we can't determine exact capacity
            if (/windows/i.test(ua) && /mobile/i.test(ua)) {
                return 'Estimated: 30-80Wh (Windows Laptop)';
            }
            
            // For mobile devices
            if (/iphone/i.test(ua)) return 'Estimated: 10-20Wh (iPhone)';
            if (/ipad/i.test(ua)) return 'Estimated: 25-40Wh (iPad)';
            if (/android/i.test(ua)) return 'Estimated: 10-25Wh (Android)';
            
            return null; // Cannot determine
        } catch (e) {
            return null;
        }
    }
    async setDeviceInfo() {
        const ua = navigator.userAgent.toLowerCase();
        if (/mobile|android|iphone|ipad|ipod/i.test(ua)) {
            const deviceInfo = await detectIndianDeviceInfo();
            this.info.device_brand = deviceInfo.brand;
            this.info.device_model = deviceInfo.model;
            this.info.os = deviceInfo.os;
            this.info.osVersion = deviceInfo.osVersion;
            this.info.deviceType = deviceInfo.deviceType;
            this.info.architecture = deviceInfo.architecture;
        } else {
            const deviceInfo = await detectDesktopDeviceInfo();
            this.info.device_brand = deviceInfo.brand;
            this.info.device_model = deviceInfo.model;
            this.info.os = deviceInfo.os;
            this.info.osVersion = deviceInfo.osVersion;
            this.info.deviceType = deviceInfo.deviceType;
            this.info.architecture = deviceInfo.architecture;
            
            // Additional attempts to detect brand for unknown Windows devices
            if (deviceInfo.brand === "Unknown" && deviceInfo.os === "Windows") {
                this.info.device_brand = await this.detectWindowsBrandFallback();
            }
        }
    }
    
    async detectWindowsBrandFallback() {
        try {
            // Try multiple detection methods for Windows brand identification
            const methods = [
                this.detectFromWebGL(),
                this.detectFromScreen(),
                this.detectFromHardware(),
                this.detectFromBrowserFingerprint()
            ];
            
            for (const method of methods) {
                const brand = await method;
                if (brand && brand !== "Unknown") {
                    return brand;
                }
            }
            
            return "Generic Windows PC";
        } catch (e) {
            return "Windows Computer";
        }
    }
    
    async detectFromWebGL() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                const renderer = gl.getParameter(gl.RENDERER);
                const vendor = gl.getParameter(gl.VENDOR);
                
                // Some GPU vendors correlate with laptop brands
                if (renderer.includes('Intel')) {
                    // Intel integrated graphics are common in business laptops
                    if (renderer.includes('UHD') || renderer.includes('Iris')) {
                        return "Intel-based Laptop";
                    }
                    return "Intel Graphics Device";
                } else if (renderer.includes('NVIDIA')) {
                    // NVIDIA often in gaming/workstation laptops
                    if (renderer.includes('RTX') || renderer.includes('GTX')) {
                        return "Gaming/Workstation PC";
                    }
                    return "NVIDIA Graphics Device";
                } else if (renderer.includes('AMD') || renderer.includes('Radeon')) {
                    return "AMD Graphics Device";
                }
            }
        } catch (e) {
            console.warn("WebGL brand detection failed", e);
        }
        return null;
    }
    
    async detectFromScreen() {
        try {
            const width = window.screen.width;
            const height = window.screen.height;
            const ratio = width / height;
            
            // Common resolutions that suggest specific device types
            if (width === 1366 && height === 768) {
                return "Budget Laptop"; // Very common in budget laptops
            } else if (width === 1920 && height === 1080) {
                return "Standard Desktop/Laptop"; // Most common resolution
            } else if (width >= 2560) {
                return "Premium/Professional Device"; // High-end displays
            } else if (ratio > 2) {
                return "Ultrawide Display Device"; // Ultrawide monitors
            }
        } catch (e) {
            console.warn("Screen-based detection failed", e);
        }
        return null;
    }
    
    async detectFromHardware() {
        try {
            const cores = navigator.hardwareConcurrency;
            const memory = navigator.deviceMemory;
            
            // Hardware-based classification
            if (cores >= 16) {
                return "High-End Workstation";
            } else if (cores >= 8) {
                return "Gaming/Performance PC";
            } else if (cores >= 4) {
                return "Standard Desktop/Laptop";
            } else {
                return "Budget/Entry-Level Device";
            }
        } catch (e) {
            console.warn("Hardware-based detection failed", e);
        }
        return null;
    }
    
    async detectFromBrowserFingerprint() {
        try {
            // Use timezone and language to suggest region-specific brands
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const language = navigator.language;
            
            if (timezone.includes('America')) {
                return "North American PC"; // Dell, HP common
            } else if (timezone.includes('Asia')) {
                return "Asian Market PC"; // ASUS, Acer common
            } else if (timezone.includes('Europe')) {
                return "European PC"; // Various brands
            }
            
            return "Regional PC";
        } catch (e) {
            console.warn("Fingerprint-based detection failed", e);
        }
        return null;
    }
    // --- New: Page visibility, focus/blur, scroll/click tracking ---
    setupEventTracking() {
        if (this._eventTrackingSetup) return;
        this._eventTrackingSetup = true;
        this.info.interaction = {
            focus: document.hasFocus(),
            blurCount: 0,
            focusCount: 0,
            scrolls: [],
            clicks: []
        };
        window.addEventListener('focus', () => {
            this.info.interaction.focus = true;
            this.info.interaction.focusCount++;
        });
        window.addEventListener('blur', () => {
            this.info.interaction.focus = false;
            this.info.interaction.blurCount++;
        });
        window.addEventListener('scroll', () => {
            this.info.interaction.scrolls.push({
                x: window.scrollX,
                y: window.scrollY,
                t: Date.now() - this.start
            });
        });
        window.addEventListener('click', (e) => {
            this.info.interaction.clicks.push({
                x: e.clientX,
                y: e.clientY,
                t: Date.now() - this.start
            });
        });
        document.addEventListener('visibilitychange', () => {
            this.info.session.pageVisibility = document.visibilityState;
        });
    }
}

// Auto-start on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startProfileGather);
} else {
    startProfileGather();
}
function startProfileGather() {
    console.log('[SystemProfile] startProfileGather called');
    setTimeout(() => {
        const profile = new SystemProfile();
        profile.setupEventTracking();
        profile.gatherAll();
    }, 100);
}

function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days*24*60*60*1000).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
}

// Add detectIndianDeviceInfo utility
async function detectIndianDeviceInfo() {
  const ua = navigator.userAgent.toLowerCase();
  const platform = (navigator.platform || '').toLowerCase();
  const uaData = navigator.userAgentData || null;

  // Show detection info on the page for mobile users
  if (/mobile|android|iphone|ipad|ipod/i.test(ua)) {
    let infoBox = document.getElementById('device-detect-info');
    if (!infoBox) {
      infoBox = document.createElement('pre');
      infoBox.id = 'device-detect-info';
      infoBox.style = 'background:#ffe;border:1px solid #ccc;padding:8px;margin:8px 0;max-width:100vw;overflow-x:auto;font-size:12px;z-index:9999;position:relative;';
      document.body.prepend(infoBox);
    }
    infoBox.textContent = 'UserAgent: ' + navigator.userAgent + '\nPlatform: ' + navigator.platform;
  }

  const result = {
    brand: "Unknown",
    model: "Unknown",
    os: "Unknown",
    osVersion: "Unknown",
    deviceType: "Unknown",
    architecture: "Unknown"
  };

  // Modern Browsers: Use User-Agent Client Hints
  if (uaData && uaData.getHighEntropyValues) {
    try {
      const hints = await uaData.getHighEntropyValues([
        "architecture",
        "model",
        "platform",
        "platformVersion",
        "fullVersionList"
      ]);

      result.architecture = hints.architecture || "Unknown";
      result.model = hints.model || "Unknown";
      result.os = hints.platform || "Unknown";
      result.osVersion = hints.platformVersion || "Unknown";
      result.deviceType = ua.includes("mobile") ? "Mobile" :
                          ua.includes("tablet") ? "Tablet" : "Desktop";

      const model = result.model.toLowerCase();

      const brandMap = {
        samsung: ["sm-", "samsung"],
        apple: ["iphone"],
        xiaomi: ["mi", "redmi", "poco"],
        vivo: ["vivo", "v", "v2", "v1", "v20", "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28", "v29", "v30", "v31", "v32", "v33", "v34", "v35", "v36", "v37", "v38", "v39", "v40", "v41", "v42", "v43", "v44", "v45", "v46", "v47", "v48", "v49", "v50"],
        oppo: ["oppo", "cph", "pclm", "pbem"],
        realme: ["realme"],
        oneplus: ["oneplus"],
        motorola: ["moto"],
        infinix: ["infinix"],
        tecno: ["tecno"],
        lava: ["lava"],
        micromax: ["micromax"],
        nokia: ["nokia"],
        iqoo: ["iqoo"]
      };

      for (const [brand, identifiers] of Object.entries(brandMap)) {
        if (identifiers.some(id => model.startsWith(id) || model.includes(id))) {
          result.brand = brand.charAt(0).toUpperCase() + brand.slice(1);
          break;
        }
      }

      return result;
    } catch (err) {
      console.warn("UA-CH not fully available", err);
    }
  }

  // Legacy UA fallback with enhanced iOS detection
  const modelRegexes = [
    { regex: /(sm-[a-z0-9]+)/, brand: "Samsung" },
    { regex: /iphone/, brand: "Apple", model: "iPhone" },
    { regex: /ipad/, brand: "Apple", model: "iPad" },
    { regex: /ipod/, brand: "Apple", model: "iPod" },
    { regex: /(redmi\s?[a-z0-9]+|mi\s?[a-z0-9]+|poco\s?[a-z0-9]+)/, brand: "Xiaomi" },
    { regex: /(vivo\s?[a-z0-9]+|v[0-9]{4,})/, brand: "Vivo" },
    { regex: /(oppo\s?[a-z0-9]+|cph[0-9]+)/, brand: "Oppo" },
    { regex: /(realme\s?[a-z0-9]+)/, brand: "Realme" },
    { regex: /(oneplus\s?[a-z0-9]+)/, brand: "OnePlus" },
    { regex: /(moto\s?[a-z0-9]+)/, brand: "Motorola" },
    { regex: /(infinix\s?[a-z0-9]+)/, brand: "Infinix" },
    { regex: /(tecno\s?[a-z0-9]+)/, brand: "Tecno" },
    { regex: /(lava\s?[a-z0-9]+)/, brand: "Lava" },
    { regex: /(micromax\s?[a-z0-9]+)/, brand: "Micromax" },
    { regex: /(nokia\s?[a-z0-9]+)/, brand: "Nokia" },
    { regex: /(iqoo\s?[a-z0-9]+)/, brand: "iQOO" }
  ];

  for (const { regex, brand, model } of modelRegexes) {
    const match = ua.match(regex) || platform.match(regex);
    if (match) {
      result.brand = brand;
      
      // Enhanced iOS model detection
      if (brand === "Apple") {
        if (ua.includes("iphone")) {
          // Try to detect iPhone model from UA string patterns
          if (ua.includes("iphone; cpu iphone os 17")) result.model = "iPhone 15 Series";
          else if (ua.includes("iphone; cpu iphone os 16")) result.model = "iPhone 14 Series";
          else if (ua.includes("iphone; cpu iphone os 15")) result.model = "iPhone 13 Series";
          else if (ua.includes("iphone; cpu iphone os 14")) result.model = "iPhone 12 Series";
          else result.model = "iPhone";
        } else if (ua.includes("ipad")) {
          if (ua.includes("ipad; cpu os 17")) result.model = "iPad (2023+)";
          else if (ua.includes("ipad; cpu os 16")) result.model = "iPad (2022)";
          else result.model = "iPad";
        } else if (ua.includes("ipod")) {
          result.model = "iPod Touch";
        }
      } else {
        result.model = model || match[1] ? match[1].toUpperCase() : "Unknown";
      }
      break;
    }
  }

  // Enhanced OS detection
  if (ua.includes("android")) {
    result.os = "Android";
    const ver = ua.match(/android\s([0-9\.]+)/);
    if (ver) result.osVersion = ver[1];
  } else if (ua.includes("iphone os") || ua.includes("ios")) {
    result.os = "iOS";
    const ver = ua.match(/iphone os ([0-9_]+)/);
    if (ver) result.osVersion = ver[1].replace(/_/g, ".");
  } else if (ua.includes("windows")) {
    result.os = "Windows";
  } else if (ua.includes("mac os x")) {
    result.os = "macOS";
  } else if (ua.includes("linux")) {
    result.os = "Linux";
  }

  // Architecture detection
  if (ua.includes("arm") || ua.includes("aarch64") || platform.includes("arm") || platform.includes("aarch64") || platform.includes("armv81")) {
    result.architecture = "ARM";
    if (document.getElementById('device-detect-info')) {
      document.getElementById('device-detect-info').textContent += '\nARCH DETECTED: ARM';
    }
  } else if (ua.includes("x86_64") || ua.includes("win64") || platform.includes("64")) {
    result.architecture = "x86_64";
    if (document.getElementById('device-detect-info')) {
      document.getElementById('device-detect-info').textContent += '\nARCH DETECTED: x86_64';
    }
  } else if (ua.includes("x86") || ua.includes("i686")) {
    result.architecture = "x86";
    if (document.getElementById('device-detect-info')) {
      document.getElementById('device-detect-info').textContent += '\nARCH DETECTED: x86';
    }
  } else {
    if (document.getElementById('device-detect-info')) {
      document.getElementById('device-detect-info').textContent += '\nARCH DETECTED: Unknown';
    }
  }

  // Device type
  if (/mobile/i.test(ua)) result.deviceType = "Mobile";
  else if (/tablet/i.test(ua)) result.deviceType = "Tablet";
  else result.deviceType = "Desktop";

  return result;
}

// Add detectDesktopDeviceInfo utility
async function detectDesktopDeviceInfo() {
  const ua = navigator.userAgent.toLowerCase();
  const platform = navigator.platform || "";
  const uaData = navigator.userAgentData || null;

  const result = {
    brand: "Unknown",
    model: "Unknown",
    os: "Unknown",
    osVersion: "Unknown",
    architecture: "Unknown",
    deviceType: "Desktop"
  };

  // Use User-Agent Client Hints if available
  if (uaData && uaData.getHighEntropyValues) {
    try {
      const hints = await uaData.getHighEntropyValues([
        "architecture",
        "platform",
        "platformVersion",
        "fullVersionList",
        "bitness",
        "wow64"
      ]);

      result.architecture = hints.architecture || hints.bitness || "Unknown";
      result.os = hints.platform || "Unknown";
      result.osVersion = hints.platformVersion || "Unknown";

      return result;
    } catch (err) {
      console.warn("UA-CH not fully supported", err);
    }
  }

  // Enhanced desktop brand detection
  const brandDetection = {
    // Apple devices
    apple: {
      patterns: [/macintosh|mac os|darwin/i, /apple/i],
      models: {
        macbook: /macbook/i,
        imac: /imac/i,
        'mac mini': /mac mini/i,
        'mac pro': /mac pro/i,
        'mac studio': /mac studio/i
      }
    },
    // Windows OEMs - Enhanced detection
    dell: {
      patterns: [/dell/i, /latitude|inspiron|optiplex|precision|xps|alienware/i],
      models: {
        inspiron: /inspiron/i,
        latitude: /latitude/i,
        optiplex: /optiplex/i,
        precision: /precision/i,
        xps: /xps/i,
        alienware: /alienware/i
      }
    },
    hp: {
      patterns: [/hp|hewlett.?packard/i, /pavilion|elitebook|probook|envy|spectre|omen/i],
      models: {
        pavilion: /pavilion/i,
        elitebook: /elitebook/i,
        probook: /probook/i,
        envy: /envy/i,
        spectre: /spectre/i,
        omen: /omen/i
      }
    },
    lenovo: {
      patterns: [/lenovo/i, /thinkpad|ideapad|yoga|legion|thinkcentre/i],
      models: {
        thinkpad: /thinkpad/i,
        ideapad: /ideapad/i,
        yoga: /yoga/i,
        legion: /legion/i,
        thinkcentre: /thinkcentre/i
      }
    },
    acer: {
      patterns: [/acer/i, /aspire|predator|swift|nitro/i],
      models: {
        aspire: /aspire/i,
        predator: /predator/i,
        swift: /swift/i,
        nitro: /nitro/i
      }
    },
    asus: {
      patterns: [/asus/i, /zenbook|vivobook|rog|tuf/i],
      models: {
        zenbook: /zenbook/i,
        vivobook: /vivobook/i,
        rog: /rog|republic.of.gamers/i,
        tuf: /tuf/i
      }
    },
    msi: {
      patterns: [/msi/i, /gaming|creator|prestige/i],
      models: {
        gaming: /gaming/i,
        creator: /creator/i,
        prestige: /prestige/i
      }
    },
    microsoft: {
      patterns: [/surface/i],
      models: {
        'surface pro': /surface pro/i,
        'surface laptop': /surface laptop/i,
        'surface book': /surface book/i,
        'surface studio': /surface studio/i
      }
    },
    // Additional brands that might appear in UA
    samsung: {
      patterns: [/samsung/i],
      models: {
        galaxy: /galaxy/i,
        notebook: /notebook/i
      }
    },
    toshiba: {
      patterns: [/toshiba/i],
      models: {
        satellite: /satellite/i,
        tecra: /tecra/i
      }
    },
    sony: {
      patterns: [/sony|vaio/i],
      models: {
        vaio: /vaio/i
      }
    },
    fujitsu: {
      patterns: [/fujitsu/i],
      models: {
        lifebook: /lifebook/i
      }
    }
  };

  // Check for brand patterns in UA and platform
  for (const [brandName, brandInfo] of Object.entries(brandDetection)) {
    const isMatch = brandInfo.patterns.some(pattern => 
      pattern.test(ua) || pattern.test(platform)
    );
    
    if (isMatch) {
      result.brand = brandName.charAt(0).toUpperCase() + brandName.slice(1);
      
      // Try to detect specific model
      for (const [modelName, modelPattern] of Object.entries(brandInfo.models)) {
        if (modelPattern.test(ua) || modelPattern.test(platform)) {
          result.model = modelName.charAt(0).toUpperCase() + modelName.slice(1);
          break;
        }
      }
      break;
    }
  }

  // Advanced brand detection for Windows machines using additional techniques
  if (result.brand === "Unknown" && ua.includes("windows")) {
    // Try to detect brand from system information hints
    try {
      // Check for OEM-specific patterns in the user agent
      const oemPatterns = {
        'Dell': [/trident.*dell/i, /edge.*dell/i],
        'HP': [/trident.*hp/i, /edge.*hp/i],
        'Lenovo': [/trident.*lenovo/i, /edge.*lenovo/i],
        'Acer': [/trident.*acer/i, /edge.*acer/i],
        'ASUS': [/trident.*asus/i, /edge.*asus/i],
        'MSI': [/trident.*msi/i, /edge.*msi/i],
        'Toshiba': [/trident.*toshiba/i, /edge.*toshiba/i],
        'Sony': [/trident.*sony/i, /edge.*sony/i, /trident.*vaio/i],
        'Samsung': [/trident.*samsung/i, /edge.*samsung/i],
        'Fujitsu': [/trident.*fujitsu/i, /edge.*fujitsu/i]
      };

      for (const [brand, patterns] of Object.entries(oemPatterns)) {
        if (patterns.some(pattern => pattern.test(ua))) {
          result.brand = brand;
          break;
        }
      }

      // If still unknown, try to use screen resolution and other hints to guess common brands
      if (result.brand === "Unknown") {
        const screenWidth = window.screen.width;
        const screenHeight = window.screen.height;
        const deviceMemory = navigator.deviceMemory;
        const cores = navigator.hardwareConcurrency;

        // Common resolution/hardware combinations that suggest specific brands
        if (screenWidth === 1366 && screenHeight === 768) {
          result.brand = "Generic Laptop"; // Very common budget laptop resolution
        } else if (screenWidth === 1920 && screenHeight === 1080) {
          if (cores >= 8) {
            result.brand = "Gaming/Workstation"; // High-end machine
          } else {
            result.brand = "Business Laptop"; // Standard business machine
          }
        } else if (screenWidth >= 2560) {
          result.brand = "Premium Device"; // High-resolution usually means premium
        } else {
          result.brand = "Standard PC"; // Generic fallback
        }
      }
    } catch (e) {
      console.warn("Advanced brand detection failed", e);
    }
  }

  // Enhanced OS detection
  if (ua.includes("windows")) {
    result.os = "Windows";
    const ver = ua.match(/windows nt ([0-9\.]+)/);
    if (ver) {
      const versionMap = {
        "10.0": "10/11",
        "6.3": "8.1",
        "6.2": "8",
        "6.1": "7",
        "6.0": "Vista",
        "5.1": "XP"
      };
      result.osVersion = versionMap[ver[1]] || ver[1];
    }
    
    // Try to detect Windows 11 specifically
    if (ua.includes("windows nt 10.0") && ua.includes("edg/")) {
      result.osVersion = "11"; // Edge often indicates Windows 11
    }
  } else if (ua.includes("mac os x") || ua.includes("darwin")) {
    result.os = "macOS";
    const ver = ua.match(/mac os x ([0-9_]+)/);
    if (ver) result.osVersion = ver[1].replace(/_/g, ".");
    
    // Detect Apple Silicon vs Intel
    if (platform.includes("arm") || ua.includes("arm64")) {
      result.architecture = "Apple Silicon (ARM)";
    } else {
      result.architecture = "Intel x86_64";
    }
  } else if (ua.includes("linux")) {
    result.os = "Linux";
    
    // Try to detect Linux distribution
    const distros = {
      ubuntu: /ubuntu/i,
      fedora: /fedora/i,
      debian: /debian/i,
      centos: /centos/i,
      'red hat': /red.?hat/i,
      opensuse: /opensuse/i,
      arch: /arch/i
    };
    
    for (const [distro, pattern] of Object.entries(distros)) {
      if (pattern.test(ua)) {
        result.osVersion = distro.charAt(0).toUpperCase() + distro.slice(1);
        break;
      }
    }
  }

  // Architecture detection with more detail
  if (!result.architecture || result.architecture === "Unknown") {
    if (ua.includes("x86_64") || ua.includes("win64") || platform.includes("64") || ua.includes("amd64")) {
      result.architecture = "x86_64";
    } else if (ua.includes("arm") || ua.includes("aarch64") || platform.includes("arm")) {
      result.architecture = "ARM64";
    } else if (ua.includes("x86") || ua.includes("i686") || ua.includes("i386")) {
      result.architecture = "x86";
    }
  }

  // Device type refinement
  if (/laptop|mobile/i.test(ua) && !ua.includes("phone")) {
    result.deviceType = "Laptop";
  } else if (/tablet/i.test(ua)) {
    result.deviceType = "Tablet";
  } else {
    result.deviceType = "Desktop";
  }

  return result;
}

// Debug function to test iOS detection
function testIOSDetection() {
    console.log('=== iOS Detection Test ===');
    console.log('User Agent:', navigator.userAgent);
    console.log('Platform:', navigator.platform);
    
    // Test browser detection
    const ua = navigator.userAgent;
    let detectedBrowser = 'Unknown';
    
    if (/iphone|ipad|ipod/i.test(ua)) {
        if (/crios/i.test(ua)) {
            detectedBrowser = 'Chrome iOS';
        } else if (/fxios/i.test(ua)) {
            detectedBrowser = 'Firefox iOS';
        } else if (/edgios/i.test(ua)) {
            detectedBrowser = 'Edge iOS';
        } else if (/opios/i.test(ua)) {
            detectedBrowser = 'Opera iOS';
        } else if (/safari/i.test(ua) || /mobile\/[0-9a-z]+$/i.test(ua)) {
            detectedBrowser = 'Safari iOS';
        }
    }
    
    console.log('Detected Browser:', detectedBrowser);
    
    // Test battery detection
    const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
    console.log('Is iOS:', isIOS);
    console.log('Battery API Available:', !!navigator.getBattery);
    
    if (isIOS) {
        console.log('✅ Battery API correctly disabled for iOS');
    }
    
    console.log('=== End Test ===');
}

// Debug function to test device detection
function testDeviceDetection() {
    console.log('=== Device Detection Test ===');
    console.log('User Agent:', navigator.userAgent);
    console.log('Platform:', navigator.platform);
    console.log('Screen:', window.screen.width + 'x' + window.screen.height);
    console.log('Hardware Concurrency:', navigator.hardwareConcurrency);
    console.log('Device Memory:', navigator.deviceMemory);
    console.log('Timezone:', Intl.DateTimeFormat().resolvedOptions().timeZone);
    
    // Test WebGL renderer
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl');
        if (gl) {
            console.log('WebGL Vendor:', gl.getParameter(gl.VENDOR));
            console.log('WebGL Renderer:', gl.getParameter(gl.RENDERER));
        }
    } catch (e) {
        console.log('WebGL not available');
    }
    
    // Test detection
    detectDesktopDeviceInfo().then(info => {
        console.log('Detected Device Info:', info);
    });
    
    console.log('=== End Test ===');
}

// Expose for testing
window.testDeviceDetection = testDeviceDetection;