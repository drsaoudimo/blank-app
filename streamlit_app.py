import streamlit as st
import numpy as np
import sympy as sp
from math import gcd, sqrt, log
import pandas as pd
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="هجوم جبري على RSA", layout="wide")

# CSS للتنسيق العربي
st.markdown("""
<style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .med-font { font-size:18px !important; }
    .arabic { direction: rtl; text-align: right; }
    .formula { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.title("🚨 الهجوم الجبري على نظام RSA")
st.markdown('<p class="big-font arabic">نموذج تعليمي يوضح مبادئ الهجوم باستخدام الغربال الجبري</p>', unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ إعدادات الهجوم")
    
    # اختيار وضع التشغيل
    mode = st.selectbox(
        "وضع التشغيل",
        ["توليد وتكسير RSA صغير", "إدخال مفتاح RSA يدوياً"]
    )
    
    if mode == "توليد وتكسير RSA صغير":
        p = st.number_input("العدد الأولي p", min_value=10, max_value=1000, value=61)
        q = st.number_input("العدد الأولي q", min_value=10, max_value=1000, value=53)
        e = st.number_input("الأس العام e", min_value=3, max_value=100, value=17)
        
        n = p * q
        phi = (p-1)*(q-1)
        
        st.markdown(f"""
        **المفتاح العام:** (n={n}, e={e})
        **المفتاح الخاص:** p={p}, q={q}
        """)
    
    else:
        n = st.number_input("أدخل قيمة n", min_value=100, max_value=100000, value=3233)
        e = st.number_input("أدخل قيمة e", min_value=3, max_value=100, value=17)
        p, q = None, None
    
    # إعدادات الهجوم
    st.header("⚡ معلمات الهجوم")
    factor_base_size = st.slider("حجم قاعدة العوامل", 5, 20, 10)
    max_relations = st.slider("الحد الأقصى للعلاقات", 20, 100, 50)
    
    if st.button("🚀 بدء الهجوم"):
        st.session_state.attack_started = True
    else:
        st.session_state.attack_started = False

# الفصل 1: مقدمة نظرية
st.markdown("---")
st.header("📚 الأساس النظري للهجوم")

with st.expander("🔍 عرض التفاصيل النظرية"):
    st.markdown("""
    ### المبدأ الرياضي للهجوم الجبري
    
    **الهدف:** تحويل مشكلة تحليل العوامل الأولية (صعبة) إلى مشكلة جبر خطي (أسهل)
    
    **الخطوات:**
    1. **بناء قاعدة عوامل أولية صغيرة:** B = {p₁, p₂, ..., pₖ}
    2. **إيجاد أعداد ناعمة:** z حيث z² mod n يتحلل إلى عوامل في B
    3. **بناء نظام معادلات خطية** فوق الحقل F₂
    4. **إيجاد متجه في النواة** (Kernel) للمصفوفة
    5. **تشكيل مربعين كاملين** واستخراج العوامل
    
    **المعادلة الأساسية:**
    
    $X^2 ≡ Y^2 \\ (mod\\ n)$
    
    $⇒ (X-Y)(X+Y) ≡ 0 \\ (mod\\ n)$
    
    $⇒ gcd(X-Y, n)$ يعطي عاملاً أولياً
    """)

# الفصل 2: تنفيذ الهجوم
if st.session_state.get('attack_started', False):
    st.markdown("---")
    st.header("⚔️ تنفيذ الهجوم الجبري")
    
    # تقدم الهجوم
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # الدالة لبناء قاعدة العوامل
    def build_factor_base(size: int, n: int) -> List[int]:
        """بناء قاعدة عوامل أولية صغيرة"""
        primes = []
        num = 2
        while len(primes) < size:
            if sp.isprime(num):
                # اختبار رمز ليجندر للتأكد من وجود جذر تربيعي mod n
                if sp.legendre_symbol(n, num) == 1:
                    primes.append(num)
            num += 1
        return primes
    
    # الدالة للتحقق من النعومة
    def is_smooth(num: int, factor_base: List[int]) -> Tuple[bool, Dict[int, int]]:
        """التحقق مما إذا كان العدد ناعماً بالنسبة لقاعدة العوامل"""
        factors = {}
        temp = num
        
        for p in factor_base:
            factors[p] = 0
            while temp % p == 0:
                factors[p] += 1
                temp //= p
        
        return temp == 1, factors
    
    # 1. بناء قاعدة العوامل
    status_text.text("🔧 الخطوة 1: بناء قاعدة العوامل الأولية...")
    progress_bar.progress(10)
    
    factor_base = build_factor_base(factor_base_size, n)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("قاعدة العوامل الأولية")
        st.write(factor_base)
        st.markdown(f"**الحجم:** {len(factor_base)} عدد أولي")
    
    with col2:
        st.subheader("التفسير")
        st.markdown("""
        يتم اختيار أعداد أولية صغيرة حيث:
        - يوجد جذر تربيعي لـ n modulo كل عدد أولي
        - تسهل عملية التحليل
        """)
    
    # 2. البحث عن الأعداد الناعمة
    status_text.text("🔍 الخطوة 2: البحث عن الأعداد الناعمة (العلاقات)...")
    progress_bar.progress(30)
    
    relations = []
    z_values = []
    
    # نطاق البحث
    search_range = int(sqrt(n)) + 100
    
    st.subheader("🔎 البحث عن العلاقات")
    relation_table_data = []
    
    for z in range(2, min(search_range, max_relations * 10)):
        value = (z * z) % n
        is_smooth_num, factors = is_smooth(value, factor_base)
        
        if is_smooth_num and value > 1:
            relations.append(factors)
            z_values.append(z)
            
            # إضافة للجدول
            relation_table_data.append({
                "z": z,
                "z² mod n": value,
                "التحليل": " × ".join([f"{p}^{exp}" for p, exp in factors.items() if exp > 0]),
                "ناعم": "✅"
            })
            
            if len(relations) >= max_relations:
                break
    
    df_relations = pd.DataFrame(relation_table_data)
    st.dataframe(df_relations, height=300)
    
    # 3. بناء المصفوفة
    status_text.text("🧮 الخطوة 3: بناء المصفوفة الثنائية...")
    progress_bar.progress(50)
    
    if len(relations) > len(factor_base):
        # بناء المصفوفة A (mod 2)
        matrix = []
        for rel in relations:
            row = [rel[p] % 2 for p in factor_base]
            matrix.append(row)
        
        A = np.array(matrix, dtype=int)
        
        st.subheader("📊 المصفوفة الثنائية A (mod 2)")
        st.write(f"الأبعاد: {A.shape[0]} صف (علاقات) × {A.shape[1]} عمود (عوامل أولية)")
        
        # عرض جزء من المصفوفة
        if A.shape[0] > 10:
            st.write("الـ 10 صفوف الأولى:")
            st.dataframe(pd.DataFrame(A[:10], columns=factor_base))
        else:
            st.dataframe(pd.DataFrame(A, columns=factor_base))
        
        # 4. إيجاد النواة (Kernel)
        status_text.text("🔢 الخطوة 4: إيجاد النواة (Kernel)...")
        progress_bar.progress(70)
        
        # حل النظام A·x = 0 (mod 2)
        # في الحقيقة، نبحث عن علاقة خطية
        st.subheader("🔍 البحث عن علاقات خطية")
        
        # محاولة إيجاد متجه في النواة
        found_solution = False
        solution_vector = None
        
        # طريقة مبسطة للبحث (لأغراض تعليمية)
        for i in range(min(1000, 2**min(10, len(relations)))):
            # توليد متجه عشوائي
            x = np.random.randint(0, 2, len(relations))
            
            # حساب A·x (mod 2)
            result = np.dot(A.T, x) % 2
            
            if np.all(result == 0) and np.any(x == 1):
                found_solution = True
                solution_vector = x
                break
        
        if found_solution:
            st.success("✅ تم إيجاد متجه في النواة!")
            st.write(f"متجه الحل: {solution_vector}")
            
            # 5. استخراج العوامل
            status_text.text("💥 الخطوة 5: استخراج العوامل الأولية...")
            progress_bar.progress(90)
            
            # حساب X و Y
            X = 1
            Y_factors = {}
            
            for idx, bit in enumerate(solution_vector):
                if bit == 1:
                    X = (X * z_values[idx]) % n
                    
                    # تجميع عوامل Y
                    for p, exp in relations[idx].items():
                        if p in Y_factors:
                            Y_factors[p] += exp
                        else:
                            Y_factors[p] = exp
            
            # حساب Y
            Y = 1
            for p, exp in Y_factors.items():
                Y = (Y * pow(p, exp // 2, n)) % n
            
            st.subheader("📐 حساب X و Y")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("X ≡ ∏ zᵢ (mod n)", X)
                st.write(f"حيث zᵢ: {[z_values[i] for i in range(len(solution_vector)) if solution_vector[i] == 1]}")
            
            with col2:
                st.metric("Y ≡ ∏ pⱼ^{eⱼ/2} (mod n)", Y)
                st.write(f"التحليل: {' × '.join([f'{p}^{exp//2}' for p, exp in Y_factors.items() if exp//2 > 0])}")
            
            # حساب gcd(X-Y, n)
            d1 = gcd(X - Y, n)
            d2 = gcd(X + Y, n)
            
            st.subheader("💣 استخراج العوامل الأولية")
            
            if d1 > 1 and d1 < n:
                st.success(f"🎉 تم كسر RSA بنجاح!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("العامل الأول p", d1)
                with col2:
                    st.metric("العامل الثاني q", n // d1)
                with col3:
                    st.metric("التحقق", "✅" if d1 * (n // d1) == n else "❌")
                
                # حساب المفتاح الخاص
                if e > 0:
                    phi = (d1 - 1) * (n // d1 - 1)
                    try:
                        d_private = pow(e, -1, phi)
                        st.info(f"**المفتاح الخاص d:** {d_private}")
                    except:
                        st.warning("لا يمكن حساب المفتاح الخاص (e و φ(n) غير أوليين)")
            
            elif d2 > 1 and d2 < n:
                st.success(f"🎉 تم كسر RSA باستخدام X+Y!")
                st.metric("العامل الأول", d2)
                st.metric("العامل الثاني", n // d2)
            
            else:
                st.warning("⚠️ لم يتم إيجاد عوامل غير بديهية")
                st.write("قد تحتاج إلى:")
                st.write("1. زيادة حجم قاعدة العوامل")
                st.write("2. زيادة عدد العلاقات")
                st.write("3. تغيير نطاق البحث")
        
        else:
            st.error("❌ لم يتم إيجاد متجه في النواة")
            st.write("**الحلول الممكنة:**")
            st.write("1. زيادة عدد العلاقات (يجب أن يكون > حجم قاعدة العوامل)")
            st.write("2. تغيير قاعدة العوامل")
            st.write("3. زيادة نطاق البحث")
    
    else:
        st.error(f"❌ عدد العلاقات ({len(relations)}) أقل من حجم قاعدة العوامل ({len(factor_base)})")
        st.write("يجب أن يكون عدد العلاقات أكبر من عدد العوامل في القاعدة لإيجاد حل")

# الفصل 3: تحليل وتفسير
st.markdown("---")
st.header("📊 تحليل النتائج")

with st.expander("📈 تحليل التعقيد الحسابي"):
    st.markdown("""
    ### تحليل تعقيد الهجوم الجبري
    
    | المرحلة | التعقيد التقريبي | الوصف |
    |---------|------------------|--------|
    | جمع العلاقات | $L_n[1/2, \\sqrt{2}]$ | البحث عن الأعداد الناعمة |
    | حل النظام الخطي | $O(m^3)$ | حيث m عدد العلاقات |
    | الذاكرة المطلوبة | $O(m^2)$ | لتخزين المصفوفة |
    
    **حيث:** $L_n[a, c] = e^{(c + o(1))(\\ln n)^a (\\ln \\ln n)^{1-a}}$
    
    ### مقارنة مع طرق أخرى:
    
    1. **القسمة التجريبية:** $O(\\sqrt{n})$ - بطيء جداً
    2. **غربال الحقل العددي:** $L_n[1/3, 1.923]$ - الأسرع للمفاتيح الكبيرة
    3. **الهجوم الجبري:** $L_n[1/2, 1]$ - متوسط السرعة
    """)

with st.expander("🛡️ دفاعات ضد الهجوم"):
    st.markdown("""
    ### كيفية حماية RSA من الهجمات الجبرية:
    
    1. **استخدام مفاتيح كبيرة كافية:**
       - 2048-bit: آمن حالياً
       - 3072-bit: موصى به للأمن طويل المدى
       - 4096-bit: لأعلى درجات الأمان
    
    2. **اختيار أعداد أولية قوية:**
       - أعداد أولية آمنة (Safe primes)
       - تجنب الأعداد الناعمة
       - استخدام توليد عشوائي قوي
    
    3. **تقنيات إضافية:**
       - Padding عشوائي (OAEP)
       - تحديث المفاتيح بانتظام
       - استخدام معايير التشفير الحديثة
    
    ### لماذا لا ينكسر RSA الحقيقي بهذه الطريقة؟
    - المفاتيح الحقيقية كبيرة جداً (أكثر من 600 رقم عشري)
    - الوقت الحسابي المطلوب يتجاوز عمر الكون
    - متطلبات الذاكرة هائلة (تيرابايتات)
    """)

# الفصل 4: معلومات إضافية
st.markdown("---")
st.header("ℹ️ معلومات إضافية")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📖 المراجع العلمية")
    st.markdown("""
    1. Pomerance, C. (1985). **The Quadratic Sieve**
    2. Lenstra, A. K., & Lenstra, H. W. (1993). **The Development of the Number Field Sieve**
    3. RSA Laboratories. **RSA Cryptography Standard**
    4. Menezes, A. J. (1996). **Handbook of Applied Cryptography**
    """)

with col2:
    st.subheader("⚠️ تحذيرات أمنية")
    st.markdown("""
    ⚠️ **هذا الكود لأغراض تعليمية فقط!**
    
    - لا يمكنه كسر مفاتيح RSA حقيقية
    - مخصص لفهم المبادئ الرياضية فقط
    - لا تستخدمه لأغراض غير قانونية
    
    **القانونية:** دراسة تقنيات كسر التشفير قانونية لأغراض بحثية وتعليمية، لكن تطبيقها على أنظمة حقيقية غير مصرح به يعتبر جريمة.
    """)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>تم تطويره لأغراض تعليمية فقط | توضيح مبادئ الهجوم الجبري على RSA</p>
    <p>⚠️ <strong>تحذير:</strong> هذا التطبيق لا يمكنه كسر مفاتيح RSA حقيقية ذات أحجام قياسية</p>
</div>
""", unsafe_allow_html=True)
