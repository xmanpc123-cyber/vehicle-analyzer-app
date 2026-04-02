import streamlit as st
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="คัดรถนำ-รถตาม", page_icon="🚘", layout="wide")

# ซ่อนปุ่ม Deploy, เมนู 3 จุด และขยับเนื้อหาขึ้นด้านบน
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
[data-testid="stHeaderActionElements"] {display: none;}
[data-testid="ManageAppBadge"] {display: none;}
[data-testid="viewerBadge"] {display: none;}
footer {visibility: hidden;}
header {background: transparent;}
.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🚘 คัดรถนำ-รถตาม")
st.markdown("วิเคราะห์หารถที่มีความเป็นไปได้ว่าเดินทางมาด้วยกัน โดยอาศัยข้อมูลจากจุดตรวจต่างๆ")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ การตั้งค่าเป้าหมาย")
    target_plate = st.text_input("ทะเบียนรถเป้าหมาย", placeholder="เช่น กอ-4213")
    provinces = [
        "กระบี่", "กรุงเทพมหานคร", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร",
        "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่",
        "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน",
        "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี",
        "พระนครศรีอยุธยา", "พะเยา", "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่",
        "ภูเก็ต", "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา",
        "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "เลย",
        "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์",
        "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี", "เบตง"
    ]
    target_province = st.selectbox("หมวดจังหวัดเป้าหมาย", options=provinces, index=None, placeholder="เลือกหรือพิมพ์ค้นหาจังหวัด...")
    
    st.divider()
    st.header("⏱️ เงื่อนไขการวิเคราะห์")
    time_window_minutes = st.slider("ช่วงเวลาที่ยอมรับได้ (นาทีก่อนและหลัง)", min_value=1, max_value=30, value=5, step=1)
    min_co_occurrences = st.slider("จำนวนจุดตรวจขั้นต่ำที่พบร่วมกัน", min_value=1, max_value=10, value=1, step=1)
    
    st.info("💡 **คำแนะนำ**: ยิ่งพบข้อมูลร่วมกันหลายจุดตรวจ โอกาสที่รถจะเดินทางมาด้วยกันยิ่งมีสูงขึ้น")

# Main Page area
st.header("📂 1. นำเข้าข้อมูลจุดตรวจ (CSV)")
st.markdown("กรุณาอัปโหลดไฟล์ CSV จากด่านตรวจต่างๆ (สามารถอัปโหลดทีละหลายไฟล์ได้)")

uploaded_files = st.file_uploader("อัปโหลดไฟล์ CSV", type="csv", accept_multiple_files=True)

if uploaded_files:
    # Read and merge all csv files
    dataframes = []
    for file in uploaded_files:
        try:
            # ทดลองอ่าน 15 บรรทัดแรกด้วย text mode เพื่อกัน error จาก pandas tokenizer
            header_row = -1
            file.seek(0)
            for i in range(15):
                line = file.readline().decode('utf-8', errors='ignore')
                if not line:
                    break
                if 'ทะเบียน' in line and 'หมวดจังหวัด' in line:
                    header_row = i
                    break
            
            file.seek(0) # กลับไปบรรทัดแรกสุด
            
            if header_row != -1:
                df = pd.read_csv(file, skiprows=header_row)
            else:
                # ฟอลแบ็คไปใช้อ่านปกติ (ข้าม error บรรทัดที่มีปัญหา)
                df = pd.read_csv(file, on_bad_lines='skip')
                
            dataframes.append(df)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์ {file.name}: {e}")
            
    if dataframes:
        # Combine data
        merged_df = pd.concat(dataframes, ignore_index=True)
        # กำจัดช่องว่างที่อาจติดมาด้วย และลบอักขระพิเศษ BOM (Byte Order Mark) ที่มักแฝงอยู่ในไฟล์ภาษาไทย
        merged_df.columns = merged_df.columns.astype(str).str.replace('\ufeff', '', regex=False).str.strip()
        
        st.success(f"อัปโหลดและรวมข้อมูลสำเร็จ! รวมข้อมูลทั้งหมด {len(merged_df)} แถว จาก {len(uploaded_files)} ด่าน")
        
        with st.expander("ดูตัวอย่างข้อมูลที่รวมกันแล้ว"):
            st.dataframe(merged_df.head(10))
            
        st.divider()
        st.header("🔍 2. ผลการวิเคราะห์")
        
        if st.button("เริ่มวิเคราะห์ข้อมูล", type="primary"):
            if not target_plate or not target_province:
                st.warning("⚠️ กรุณาระบุ ทะเบียนรถ และ หมวดจังหวัดเป้าหมาย ก่อนเริ่มการวิเคราะห์")
            else:
                try:
                    # Check required columns
                    required_columns = ['ทะเบียน', 'หมวดจังหวัด', 'จุดตรวจ', 'วันเวลา']
                    missing_cols = [col for col in required_columns if col not in merged_df.columns]
                    if missing_cols:
                        st.error(f"ไฟล์ CSV ขาดคอลัมน์ที่จำเป็น: {', '.join(missing_cols)}")
                    else:
                        with st.spinner('กำลังวิเคราะห์...'):
                            # Convert date
                            merged_df['วันเวลา'] = pd.to_datetime(merged_df['วันเวลา'], format='%H:%M:%S %d/%m/%Y', errors='coerce')
                            merged_df = merged_df.dropna(subset=['วันเวลา'])
                            merged_df = merged_df.sort_values(by='วันเวลา')

                            # Filter Target target
                            target_data = merged_df[(merged_df['ทะเบียน'] == target_plate) & (merged_df['หมวดจังหวัด'] == target_province)]

                            if target_data.empty:
                                st.warning(f"ไม่พบข้อมูลของรถ ทะเบียน '{target_plate} {target_province}' ในระบบ")
                            else:
                                st.write(f"**พบข้อมูลรถเป้าหมาย {target_plate} {target_province} จำนวน {len(target_data)} ครั้ง:**")
                                st.dataframe(target_data[['จุดตรวจ', 'วันเวลา']].reset_index(drop=True))

                                companions = {}
                                time_window = timedelta(minutes=time_window_minutes)

                                for _, target_row in target_data.iterrows():
                                    checkpoint = target_row['จุดตรวจ']
                                    target_time = target_row['วันเวลา']

                                    start_time = target_time - time_window
                                    end_time = target_time + time_window

                                    mask = (
                                        (merged_df['จุดตรวจ'] == checkpoint) &
                                        (merged_df['วันเวลา'] >= start_time) &
                                        (merged_df['วันเวลา'] <= end_time) &
                                        ~((merged_df['ทะเบียน'] == target_plate) & (merged_df['หมวดจังหวัด'] == target_province))
                                    )

                                    potential_companions = merged_df[mask]

                                    for _, companion_row in potential_companions.iterrows():
                                        plate = companion_row['ทะเบียน']
                                        province = companion_row['หมวดจังหวัด']
                                        key = f"{plate} {province}"
                                        
                                        c_time = companion_row['วันเวลา']
                                        
                                        # Determine if leading or following
                                        is_lead = c_time < target_time
                                        is_follow = c_time > target_time

                                        if key not in companions:
                                            companions[key] = {
                                                'ทะเบียน': plate,
                                                'หมวดจังหวัด': province,
                                                'ยี่ห้อ': companion_row.get('ยี่ห้อรถ', ''),
                                                'รุ่น': companion_row.get('รุ่นรถ', ''),
                                                'สี': companion_row.get('สีรถ', ''),
                                                'จำนวนครั้งที่พบ': 0,
                                                'จำนวนนำ': 0,
                                                'จำนวนตาม': 0,
                                                'พฤติกรรม': '',
                                                'รายละเอียดจุดตรวจ': []
                                            }
                                        
                                        companions[key]['จำนวนครั้งที่พบ'] += 1
                                        if is_lead: companions[key]['จำนวนนำ'] += 1
                                        if is_follow: companions[key]['จำนวนตาม'] += 1
                                        
                                        diff_seconds = int((c_time - target_time).total_seconds())
                                        abs_sec = abs(diff_seconds)
                                        m, s = divmod(abs_sec, 60)
                                        
                                        time_text = ""
                                        if m > 0 and s > 0:
                                            time_text = f"{m} นาที {s} วิ."
                                        elif m > 0:
                                            time_text = f"{m} นาที"
                                        elif s > 0:
                                            time_text = f"{s} วิ."
                                            
                                        if diff_seconds < 0:
                                            diff_str = f"นำ {time_text}"
                                        elif diff_seconds > 0:
                                            diff_str = f"ตาม {time_text}"
                                        else:
                                            diff_str = "พร้อมกัน"
                                            
                                        companions[key]['รายละเอียดจุดตรวจ'].append(f"{checkpoint} ({c_time.strftime('%H:%M:%S')} {diff_str})")

                                # Determine behavior and filter by min_co_occurrences
                                filtered_companions = []
                                for k, v in companions.items():
                                    if v['จำนวนครั้งที่พบ'] >= min_co_occurrences:
                                        if v['จำนวนนำ'] == v['จำนวนครั้งที่พบ']:
                                            v['พฤติกรรม'] = 'ผู้นำทาง (Leading)'
                                        elif v['จำนวนตาม'] == v['จำนวนครั้งที่พบ']:
                                            v['พฤติกรรม'] = 'ผู้ตาม (Following)'
                                        else:
                                            v['พฤติกรรม'] = 'สลับกันนำ/ตาม (Mixed)'
                                        filtered_companions.append(v)

                                if not filtered_companions:
                                    st.info("ℹ️ ไม่พบรถที่มีแนวโน้มเดินทางมาด้วยกันตามเงื่อนไขที่กำหนด")
                                else:
                                    st.success(f"🎉 พบรถที่มีแนวโน้มเดินทางมาด้วยกันทั้งหมด {len(filtered_companions)} คัน!")
                                    
                                    # Sort by occurrences desc
                                    filtered_companions.sort(key=lambda x: x['จำนวนครั้งที่พบ'], reverse=True)
                                    result_df = pd.DataFrame(filtered_companions)
                                    result_df['รายละเอียดจุดตรวจ'] = result_df['รายละเอียดจุดตรวจ'].apply(lambda x: " | ".join(x))
                                    columns_to_show = ['ทะเบียน', 'หมวดจังหวัด', 'พฤติกรรม', 'จำนวนนำ', 'จำนวนตาม', 'จำนวนครั้งที่พบ', 'รายละเอียดจุดตรวจ']
                                    
                                    # Split data
                                    leaders_df = result_df[result_df['พฤติกรรม'] == 'ผู้นำทาง (Leading)']
                                    followers_df = result_df[result_df['พฤติกรรม'] == 'ผู้ตาม (Following)']
                                    
                                    # Create Tabs
                                    tab1, tab2, tab3 = st.tabs([
                                        f"📊 ทั้งหมด ({len(result_df)})", 
                                        f"🏎️ รถนำตลอดทาง ({len(leaders_df)})", 
                                        f"🚓 รถตามตลอดทาง ({len(followers_df)})"
                                    ])
                                    
                                    with tab1:
                                        st.table(result_df[columns_to_show])
                                    with tab2:
                                        if leaders_df.empty:
                                            st.info("ไม่มีรถที่เป็นผู้นำตลอดเส้นทาง")
                                        else:
                                            st.table(leaders_df[columns_to_show])
                                    with tab3:
                                        if followers_df.empty:
                                            st.info("ไม่มีรถที่เป็นผู้ตามตลอดเส้นทาง")
                                        else:
                                            st.table(followers_df[columns_to_show])

                except Exception as e:
                    st.error(f"เกิดข้อพิดพลาดระหว่างการประมวลผล: {e}")
else:
    st.info("👈 กรุณาอัปโหลดไฟล์ CSV เพื่อเริ่มต้นใช้งาน")
