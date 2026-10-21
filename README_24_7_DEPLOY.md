# 24/7 CLOUD HOSTING GUIDE (LAPTOP-OFF PERMANENT ACCESS)

Ab aapko apna laptop on rakhne ki zaroorat nahi hai. Niche diye gaye kisi bhi free cloud platform par 2 minute me deploy karke aap permanent free live link le sakte hain jo phone se 24/7 chalega chahe laptop band ho.

---

### Option 1: Render.com (Recommended - 100% Free & Automatic)
1. **GitHub** par ek naya private/public repo banaye (e.g. `trx-strategy2-portal`).
2. Is `cloud_deployment` folder ke saare files (`app.py`, `Dockerfile`, `requirements.txt`, `Procfile`, `render.yaml`) us repo me upload kar de.
3. [Render.com](https://render.com) par free account banaye.
4. **New +** -> **Web Service** -> Apna GitHub repository select kare.
5. Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Plan: **Free ($0/month)**
6. **Create Web Service** par click kare.
7. 2 minute me aapko permanent link mil jayega:
   `https://trx-strategy2-portal.onrender.com`
   *(Ye link 24/7 live rahega, chahe aapka laptop off ho ya travel kar rahe ho!)*

---

### Option 2: Hugging Face Spaces (Zero Sleep - 100% Free Permanent)
1. [Hugging Face](https://huggingface.co) par free account banaye.
2. **New Space** par click kare.
3. Space SDK: **Docker** (Blank) select kare.
4. Repo me `Dockerfile`, `app.py`, `requirements.txt` upload kar de.
5. Hugging Face instantly container start kar dega aur permanent direct URL dega:
   `https://yourusername-trx-strategy2.hf.space`

---

### Option 3: Koyeb / Railway
- Koyeb par `Dockerfile` ke sath free tier me 1 micro instance 24/7 continuous runs without sleeping.
