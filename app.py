import streamlit as st
import json
import os


def load_data(filepath):
    """Memuat data dari file JSON."""
    if not os.path.exists(filepath):
        
        if "symptoms" in filepath:
            return [] 
        elif "rules" in filepath:
            return {} 
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error(f"Error: File {filepath} rusak atau format JSON tidak valid. Menggunakan data kosong.")
        if "symptoms" in filepath:
            return []
        elif "rules" in filepath:
            return {}
    except Exception as e:
        st.error(f"Error saat memuat {filepath}: {e}")
        if "symptoms" in filepath:
            return []
        elif "rules" in filepath:
            return {}


def save_data(filepath, data):
    """Menyimpan data ke file JSON."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saat menyimpan {filepath}: {e}")


DATA_DIR = 'data'
SYMPTOMS_FILE = os.path.join(DATA_DIR, 'symptoms.json')
RULES_FILE = os.path.join(DATA_DIR, 'rules.json')


if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    
    save_data(SYMPTOMS_FILE, [])
    save_data(RULES_FILE, {})



if 'txtgejala_raw' not in st.session_state:
    st.session_state.txtgejala_raw = load_data(SYMPTOMS_FILE)
   
    st.session_state.txtgejala = [f"{s['id'].replace('G','').lstrip('0')}. {s['name']}" for s in st.session_state.txtgejala_raw]


if 'penyakit_raw' not in st.session_state:
    st.session_state.penyakit_raw = load_data(RULES_FILE)
    st.session_state.penyakit = list(st.session_state.penyakit_raw.keys()) # Hanya nama penyakit


if 'bagansakit' not in st.session_state:
    
    
    
    symptom_id_to_index = {s['id']: i for i, s in enumerate(st.session_state.txtgejala_raw)}
    
    st.session_state.bagansakit = [] 
    for disease_name in st.session_state.penyakit:
        rule_symptom_ids = st.session_state.penyakit_raw.get(disease_name, [])
        
        rule_symptom_indices = [symptom_id_to_index[sid] for sid in rule_symptom_ids if sid in symptom_id_to_index]
        st.session_state.bagansakit.append(rule_symptom_indices)



bagangejala = [
    [1, 2, 4, 5], [4, 5, 6], [4, 7], [4, 8, 9], [8, 10],
    [4, 5, 9, 11], [4, 8, 11, 12], [4, 13], [1, 2, 3, 4],
    [14, 15], [14, 16], [14, 17], [18, 19]
]



st.set_page_config(layout="wide", page_title="Sistem Pakar Gastro-Usus")

st.title("👨‍⚕️ Sistem Pakar Diagnosis Gangguan Gastro-Usus")
st.markdown("Aplikasi ini membantu mendiagnosis gangguan gastro-usus berdasarkan gejala yang Anda alami dan memungkinkan pakar untuk memodifikasi data.")


tab1, tab2 = st.tabs(["🩺 Diagnosis", "⚙️ Modifikasi Data Pakar"])

with tab1: 
    st.header("Pilih Gejala Anda:")
    st.markdown("---")

    
    selected_symptom_indices = []
    
   
    if not st.session_state.txtgejala_raw:
        st.info("Tidak ada data gejala. Silakan masuk ke 'Modifikasi Data Pakar' untuk menambahkan gejala.")
    else:
        cols = st.columns(3) 
        for i, gejala_obj in enumerate(st.session_state.txtgejala_raw):
            with cols[i % 3]:
                if st.checkbox(gejala_obj['name'], key=f"gejala_checkbox_{gejala_obj['id']}"):
                    selected_symptom_indices.append(i) # Tambahkan indeks 0-based


    st.markdown("---")
    st.subheader("Atur Ambang Batas Kecocokan (%):")
    
    input_threshold = st.slider("Threshold", min_value=0.0, max_value=100.0, value=20.0, step=1.0, format="%.1f%%")

    st.markdown("---")

    
    if st.button("Proses Diagnosis", type="primary", use_container_width=True):
      
        if not selected_symptom_indices:
            st.warning("⚠️ Harap pilih setidaknya satu gejala untuk diagnosis.")
        elif not st.session_state.bagansakit:
            st.warning("⚠️ Tidak ada aturan penyakit. Silakan masuk ke 'Modifikasi Data Pakar' untuk menambahkan aturan.")
        else:
            st.subheader("Hasil Analisa:")
            hasil_analisa = []

           
            for idx_penyakit, gejala_penyakit_indices in enumerate(st.session_state.bagansakit):
                gejala_terpilih_count = 0
                total_gejala_penyakit = len(gejala_penyakit_indices)

                
                if total_gejala_penyakit == 0:
                    percentage = 0.0
                else:
                    for gejala_index_di_penyakit in gejala_penyakit_indices:
                        
                        if gejala_index_di_penyakit < len(st.session_state.txtgejala_raw) and \
                           gejala_index_di_penyakit in selected_symptom_indices:
                            gejala_terpilih_count += 1

                    percentage = (gejala_terpilih_count / total_gejala_penyakit) * 100

                
                if percentage >= input_threshold:
                    hasil_analisa.append(f"✅ **{st.session_state.penyakit[idx_penyakit]}**: {percentage:.2f}% (Cocok)")
                else:
                    hasil_analisa.append(f"❌ **{st.session_state.penyakit[idx_penyakit]}**: {percentage:.2f}% (Tidak Cocok)")

            
            if hasil_analisa:
                for hasil in hasil_analisa:
                    st.write(hasil)
            else:
                st.info("ℹ️ Tidak ada penyakit yang terdeteksi berdasarkan gejala dan threshold yang dipilih.")

with tab2: 
    st.header("⚙️ Modifikasi Data Sistem Pakar")
    st.markdown("Di sini Anda dapat menambah, memodifikasi, atau menghapus data gejala dan aturan penyakit.")
    st.info("📝 Perubahan yang Anda lakukan di sini akan **disimpan secara otomatis** ke file JSON.")

    st.subheader("Manajemen Gejala")
    with st.expander("➕ **Tambah/Kelola Gejala**", expanded=False):
       
        new_symptom_id = st.text_input("ID Gejala Baru (Contoh: G020)", key="new_symptom_id_input").strip().upper()
       
        new_symptom_name = st.text_input("Nama Gejala Baru (Contoh: Kram Perut)", key="new_symptom_name_input").strip()

        col_add_symptom, col_delete_symptom_btn = st.columns(2)

        with col_add_symptom:
            if st.button("➕ Tambah Gejala", key="add_symptom_btn", use_container_width=True):
                if new_symptom_id and new_symptom_name:
                    if any(s['id'] == new_symptom_id for s in st.session_state.txtgejala_raw):
                        st.error(f"ID Gejala '{new_symptom_id}' sudah ada. Gunakan ID lain.")
                    else:
                        st.session_state.txtgejala_raw.append({"id": new_symptom_id, "name": new_symptom_name})
                        st.session_state.txtgejala.append(f"{len(st.session_state.txtgejala)}. {new_symptom_name}") # Update formatted list
                        
                        save_data(SYMPTOMS_FILE, st.session_state.txtgejala_raw)
                        st.success(f"✅ Gejala '{new_symptom_name}' (ID: {new_symptom_id}) berhasil ditambahkan!")
                        st.rerun()
                else:
                    st.error("ID dan Nama Gejala tidak boleh kosong.")
        
        st.markdown("---")
        st.info("Daftar Gejala Saat Ini:")
        if st.session_state.txtgejala_raw:
            st.dataframe(st.session_state.txtgejala_raw, use_container_width=True)
            
           
            symptom_options_for_delete = [""] + [f"{s['id']} - {s['name']}" for s in st.session_state.txtgejala_raw]
            selected_symptom_to_delete_display = st.selectbox(
                "Pilih Gejala yang ingin dihapus:",
                symptom_options_for_delete,
                key="delete_symptom_select"
            )

            if selected_symptom_to_delete_display and selected_symptom_to_delete_display != "":
                symptom_id_to_delete = selected_symptom_to_delete_display.split(' - ')[0]
                symptom_name_to_delete = selected_symptom_to_delete_display.split(' - ')[1]
                
                with col_delete_symptom_btn:
                    if st.button("🗑️ Hapus Gejala", key="delete_symptom_btn", use_container_width=True):
                       
                        st.session_state.txtgejala_raw = [s for s in st.session_state.txtgejala_raw if s['id'] != symptom_id_to_delete]
                       
                        st.session_state.txtgejala = [f"{s['id'].replace('G','').lstrip('0')}. {s['name']}" for s in st.session_state.txtgejala_raw]

                       
                        new_bagansakit = []
                        new_penyakit = []
                        new_penyakit_raw = {}
                        
                       
                        new_symptom_id_to_index = {s['id']: i for i, s in enumerate(st.session_state.txtgejala_raw)}

                        for disease_name, rule_symptom_ids in st.session_state.penyakit_raw.items():
                            updated_rule_symptom_ids = [sid for sid in rule_symptom_ids if sid != symptom_id_to_delete]
                           
                            updated_rule_symptom_indices = [new_symptom_id_to_index[sid] for sid in updated_rule_symptom_ids if sid in new_symptom_id_to_index]
                            
                            new_penyakit_raw[disease_name] = updated_rule_symptom_ids 
                            new_bagansakit.append(updated_rule_symptom_indices) 
                            new_penyakit.append(disease_name) 

                        st.session_state.penyakit_raw = new_penyakit_raw
                        st.session_state.penyakit = new_penyakit
                        st.session_state.bagansakit = new_bagansakit 
                        save_data(SYMPTOMS_FILE, st.session_state.txtgejala_raw)
                        save_data(RULES_FILE, st.session_state.penyakit_raw)
                        st.success(f"✅ Gejala '{symptom_name_to_delete}' (ID: {symptom_id_to_delete}) berhasil dihapus!")
                        st.rerun()
        else:
            st.info("Belum ada gejala yang terdaftar.")


    st.subheader("Manajemen Aturan Penyakit")
    with st.expander("📝 **Tambah/Modifikasi Aturan Penyakit**", expanded=True):
      
        current_diseases_options = ["--- Tambah Penyakit Baru ---"] + st.session_state.penyakit
        selected_disease_for_edit = st.selectbox(
            "Pilih Penyakit untuk Dimodifikasi/Ditambahkan:",
            current_diseases_options,
            key="select_disease_edit"
        )

        disease_name_input = ""
        is_new_disease = False

        if selected_disease_for_edit == "--- Tambah Penyakit Baru ---":
            is_new_disease = True
            disease_name_input = st.text_input("Nama Penyakit Baru", key="new_disease_name_input")
        else:
            is_new_disease = False
            disease_name_input = selected_disease_for_edit 

        
        current_symptoms_for_disease_ids = []
        if not is_new_disease:
            current_symptoms_for_disease_ids = st.session_state.penyakit_raw.get(selected_disease_for_edit, [])
        
        
        all_symptom_options_names = [s['name'] for s in st.session_state.txtgejala_raw] 
        symptom_name_to_id = {s['name']: s['id'] for s in st.session_state.txtgejala_raw} 
        current_symptoms_for_disease_names = [
            s['name'] for s in st.session_state.txtgejala_raw
            if s['id'] in current_symptoms_for_disease_ids
        ]

        
        selected_symptoms_for_rule_names = st.multiselect(
            "Pilih Gejala yang Terkait dengan Penyakit Ini:",
            options=all_symptom_options_names,
            default=current_symptoms_for_disease_names,
            key="symptoms_for_rule_multiselect"
        )

        
        selected_symptoms_for_rule_ids = [symptom_name_to_id[name] for name in selected_symptoms_for_rule_names]

        col_save_rule, col_delete_rule = st.columns(2)

        with col_save_rule:
            if st.button("💾 Simpan Aturan Penyakit", key="save_rule_btn", use_container_width=True):
                if not disease_name_input:
                    st.error("Nama penyakit tidak boleh kosong.")
                elif not selected_symptoms_for_rule_ids:
                    st.warning("Pilih setidaknya satu gejala untuk aturan penyakit ini.")
                else:
                    
                    st.session_state.penyakit_raw[disease_name_input.strip()] = selected_symptoms_for_rule_ids

                    
                    st.session_state.penyakit = list(st.session_state.penyakit_raw.keys())
                    
                   
                    st.session_state.bagansakit = []
                    current_symptom_id_to_index = {s['id']: i for i, s in enumerate(st.session_state.txtgejala_raw)}
                    for disease in st.session_state.penyakit:
                        rule_ids = st.session_state.penyakit_raw.get(disease, [])
                        indices = [current_symptom_id_to_index[sid] for sid in rule_ids if sid in current_symptom_id_to_index]
                        st.session_state.bagansakit.append(indices)

                    save_data(RULES_FILE, st.session_state.penyakit_raw)
                    st.success(f"✅ Aturan untuk '{disease_name_input}' berhasil disimpan/diperbarui!")
                    st.rerun()
        
        st.markdown("---")
        st.info("Daftar Aturan Penyakit Saat Ini:")
        if st.session_state.penyakit:
            display_rules = []
            for i, disease in enumerate(st.session_state.penyakit):
                
                symptom_ids = st.session_state.penyakit_raw.get(disease, [])
                
               
                symptom_names = [
                    s['name'] for s in st.session_state.txtgejala_raw
                    if s['id'] in symptom_ids
                ]
                display_rules.append({"Penyakit": disease, "Gejala Terkait": ", ".join(symptom_names) if symptom_names else "Tidak ada gejala terkait"})
            st.dataframe(display_rules, use_container_width=True)
        else:
            st.info("Belum ada aturan yang terdaftar.")
        
        
        if st.session_state.penyakit:
            st.markdown("---")
            st.subheader("Hapus Penyakit")
            disease_to_delete = st.selectbox(
                "Pilih Penyakit untuk Dihapus:",
                [""] + st.session_state.penyakit, 
                key="delete_disease_select"
            )
            if disease_to_delete and disease_to_delete != "":
                with col_delete_rule:
                    if st.button("🗑️ Hapus Penyakit Ini", key="delete_disease_btn", use_container_width=True):
                        if disease_to_delete in st.session_state.penyakit_raw:
                            del st.session_state.penyakit_raw[disease_to_delete]
                            
                            
                            st.session_state.penyakit = list(st.session_state.penyakit_raw.keys())
                            st.session_state.bagansakit = []
                            current_symptom_id_to_index = {s['id']: i for i, s in enumerate(st.session_state.txtgejala_raw)}
                            for disease in st.session_state.penyakit:
                                rule_ids = st.session_state.penyakit_raw.get(disease, [])
                                indices = [current_symptom_id_to_index[sid] for sid in rule_ids if sid in current_symptom_id_to_index]
                                st.session_state.bagansakit.append(indices)

                            save_data(RULES_FILE, st.session_state.penyakit_raw)
                            st.success(f"✅ Penyakit '{disease_to_delete}' berhasil dihapus.")
                            st.rerun()
                        else:
                            st.error("Penyakit tidak ditemukan.")
            else:
                st.info("Pilih penyakit yang ingin dihapus.")


st.markdown("---")
st.markdown("Aplikasi Sistem Pakar Diagnosis Gangguan Gastro-Usus By Mu'adz Al Barki (農Mikoto).")
