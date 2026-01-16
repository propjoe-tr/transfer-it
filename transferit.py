#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from playwright.sync_api import sync_playwright
import sys
import os
import time


def get_download_link(page):
    download_link = None
    try:
        inputs = page.locator('input[type="text"], input[readonly]').all()
        for inp in inputs:
            value = inp.input_value()
            if value and 'transfer.it/t/' in value:
                download_link = value
                break
    except:
        pass
    
    if not download_link:
        try:
            clipboard_button = page.locator('button.js-copy-to-clipboard')
            if clipboard_button.is_visible():
                clipboard_button.click()
                time.sleep(0.5)
                download_link = page.evaluate('navigator.clipboard.readText()')
        except:
            pass
    
    if not download_link:
        current_url = page.url
        if 'transfer.it/t/' in current_url:
            download_link = current_url
    
    return download_link.strip() if download_link else None


def wait_for_upload(page, start_time, timeout=7200):
    last_progress = 0
    last_displayed_progress = 0
    last_progress_time = time.time()
    
    def handle_console(msg):
        nonlocal last_progress, last_progress_time, last_displayed_progress
        text = msg.text
        
        if 'ul-progress' in text:
            parts = text.split()
            for i, part in enumerate(parts):
                if part.isdigit() and i > 0 and parts[i-1] == 'ul_2048':
                    progress = int(part)
                    if progress > last_progress:
                        last_progress = progress
                        last_progress_time = time.time()
                        
                        if progress % 10 == 0 and progress != last_displayed_progress:
                            last_displayed_progress = progress
                            elapsed = int(time.time() - start_time)
                            print(f"   [*] Progress: {progress}% | Gecen sure: {elapsed // 60}dk {elapsed % 60}sn")
                    break
    
    page.on('console', handle_console)
    
    while (time.time() - start_time) < timeout:
        try:
            if last_progress >= 100:
                print("   [+] Progress 100% - Upload tamamlandi!")
                return True
            
            if page.locator('text=Completed!').is_visible():
                print("   [+] 'Completed!' bulundu!")
                return True
            
            if last_progress > 0 and (time.time() - last_progress_time) > 300:
                print(f"   [!] Progress {last_progress}%'de 5 dakikadir takili!")
            
            time.sleep(5)
        except:
            time.sleep(5)
    
    print("[!] Timeout! Upload cok uzun surdu.")
    return False


def upload_single_file(page, file_path):
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    file_name = os.path.basename(file_path)
    
    print(f"\n{'-'*60}")
    print(f"[*] Dosya: {file_name}")
    print(f"[*] Boyut: {file_size_mb:.2f} MB")
    print(f"{'-'*60}")
    
    try:
        print("[*] Transfer.it'e baglaniliyor...")
        page.goto('https://transfer.it', wait_until='networkidle', timeout=30000)
        
        print("[*] Dosya seciliyor...")
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(file_path)
        time.sleep(1)
        
        print("[*] Transfer baslatiliyor...")
        transfer_button = page.locator('button.js-get-link-button')
        transfer_button.wait_for(state='visible', timeout=10000)
        transfer_button.click()
        
        print("[*] Upload devam ediyor...")
        start_time = time.time()
        
        if not wait_for_upload(page, start_time):
            return None
        
        print("[+] Upload tamamlandi!")
        print("[*] Link butonu bekleniyor...")
        
        copy_button = page.locator('button.js-copy-link')
        copy_button.wait_for(state='visible', timeout=0)
        print("[*] Link aliniyor...")
        copy_button.click()
        page.wait_for_load_state('networkidle', timeout=0)
        
        download_link = get_download_link(page)
        
        if download_link:
            print(f"[+] Link alindi!")
            print(f"[*] {download_link}")
            
            link_file = f"{file_name}.link.txt"
            with open(link_file, 'w', encoding='utf-8') as f:
                f.write(f"Dosya: {file_name}\n")
                f.write(f"Boyut: {file_size_mb:.2f} MB\n")
                f.write(f"Link: {download_link}\n")
                f.write(f"Tarih: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"[+] Link kaydedildi: {link_file}")
            return download_link
        else:
            print("[!] Link alinamadi!")
            return None
            
    except Exception as e:
        print(f"[-] Hata: {e}")
        return None


def upload_multiple_files(page, file_paths):
    total_size = sum(os.path.getsize(f) for f in file_paths)
    total_size_mb = total_size / (1024 * 1024)
    total_size_gb = total_size_mb / 1024
    
    print(f"\n{'-'*60}")
    print(f"[*] Toplam {len(file_paths)} dosya birlikte upload edilecek")
    print(f"[*] Toplam boyut: {total_size_gb:.2f} GB ({total_size_mb:.2f} MB)")
    print(f"{'-'*60}")
    
    for i, fp in enumerate(file_paths, 1):
        size_mb = os.path.getsize(fp) / (1024 * 1024)
        print(f"  {i}. {os.path.basename(fp)} ({size_mb:.2f} MB)")
    
    print(f"{'-'*60}")
    
    try:
        print("\n[*] Transfer.it'e baglaniliyor...")
        page.goto('https://transfer.it', wait_until='networkidle', timeout=30000)
        
        print("[*] Dosyalar seciliyor...")
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(file_paths)
        time.sleep(2)
        
        print("[*] Transfer baslatiliyor...")
        transfer_button = page.locator('button.js-get-link-button')
        transfer_button.wait_for(state='visible', timeout=10000)
        transfer_button.click()
        
        print("[*] Upload devam ediyor...")
        print("   (Birden fazla dosya icin bu islem uzun surebilir)\n")
        start_time = time.time()
        
        if not wait_for_upload(page, start_time):
            return None
        
        print("[+] Upload tamamlandi!")
        print("[*] Link butonu bekleniyor...")
        
        copy_button = page.locator('button.js-copy-link')
        copy_button.wait_for(state='visible', timeout=0)
        print("[*] Link aliniyor...")
        copy_button.click()
        page.wait_for_load_state('networkidle', timeout=0)
        
        download_link = get_download_link(page)
        
        if download_link:
            print(f"[+] Link alindi!")
            print(f"[*] {download_link}")
            
            link_file = f"multiple_files_{int(time.time())}.link.txt"
            with open(link_file, 'w', encoding='utf-8') as f:
                f.write(f"Toplam dosya sayisi: {len(file_paths)}\n")
                f.write(f"Toplam boyut: {total_size_gb:.2f} GB\n")
                f.write(f"Link: {download_link}\n")
                f.write(f"Tarih: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("Dosyalar:\n")
                for i, fp in enumerate(file_paths, 1):
                    size_mb = os.path.getsize(fp) / (1024 * 1024)
                    f.write(f"  {i}. {os.path.basename(fp)} ({size_mb:.2f} MB)\n")
            
            print(f"[+] Link kaydedildi: {link_file}")
            return download_link
        else:
            print("[!] Link alinamadi!")
            return None
            
    except Exception as e:
        print(f"[-] Hata: {e}")
        import traceback
        traceback.print_exc()
        return None


def upload_files(file_paths, together=True):
    print(f"\n{'='*60}")
    print(f"[*] Transfer.it Upload Tool")
    print(f"{'='*60}")
    print(f"[*] Toplam dosya sayisi: {len(file_paths)}")
    
    if together and len(file_paths) > 1:
        print(f"[*] Mod: Tum dosyalar tek link altinda")
    else:
        print(f"[*] Mod: Her dosya ayri link")
    
    print(f"{'='*60}")
    
    results = []
    
    with sync_playwright() as p:
        print("\n[*] Browser baslatiliyor...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        
        if together and len(file_paths) > 1:
            valid_files = [fp for fp in file_paths if os.path.exists(fp)]
            invalid_files = [fp for fp in file_paths if not os.path.exists(fp)]
            
            for fp in invalid_files:
                print(f"[-] Dosya bulunamadi: {fp}")
            
            if valid_files:
                link = upload_multiple_files(page, valid_files)
                results.append((valid_files, link))
        else:
            for i, file_path in enumerate(file_paths, 1):
                print(f"\n{'='*60}")
                print(f"[*] Dosya {i}/{len(file_paths)}")
                print(f"{'='*60}")
                
                if not os.path.exists(file_path):
                    print(f"[-] Dosya bulunamadi: {file_path}")
                    results.append((file_path, None))
                    continue
                
                link = upload_single_file(page, file_path)
                results.append((file_path, link))
                
                if i < len(file_paths):
                    time.sleep(2)
        
        browser.close()
    
    print(f"\n{'='*60}")
    print(f"[*] OZET")
    print(f"{'='*60}")
    
    if together and len(file_paths) > 1:
        if results and results[0][1]:
            print(f"[+] Basarili: Tum dosyalar upload edildi")
            print(f"\n[*] Download Link:")
            print(f"    {results[0][1]}")
        else:
            print(f"[-] Upload basarisiz")
    else:
        success_count = sum(1 for _, link in results if link)
        fail_count = len(results) - success_count
        
        print(f"[+] Basarili: {success_count}")
        print(f"[-] Basarisiz: {fail_count}")
        print(f"\n[*] Detaylar:")
        
        for file_path, link in results:
            if isinstance(file_path, list):
                if link:
                    print(f"  [+] {len(file_path)} dosya -> {link}")
                else:
                    print(f"  [-] {len(file_path)} dosya -> HATA")
            else:
                file_name = os.path.basename(file_path)
                if link:
                    print(f"  [+] {file_name} -> {link}")
                else:
                    print(f"  [-] {file_name} -> HATA")
    
    print(f"{'='*60}\n")
    return results


def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("[*] Transfer.it CLI - Kullanim")
        print("="*60)
        print("\nTek dosya:")
        print("  py transferit.py <dosya_yolu>")
        print("\nBirden fazla dosya (tek link):")
        print("  py transferit.py <dosya1> <dosya2> <dosya3>")
        print("\nBirden fazla dosya (ayri linkler):")
        print("  py transferit.py --separate <dosya1> <dosya2> <dosya3>")
        print("\nOrnekler:")
        print("  py transferit.py myfile.zip")
        print("  py transferit.py file1.zip file2.pdf file3.mp4")
        print("  py transferit.py --separate file1.zip file2.pdf")
        print("="*60 + "\n")
        sys.exit(1)
    
    together = True
    file_paths = sys.argv[1:]
    
    if '--separate' in file_paths:
        together = False
        file_paths.remove('--separate')
    
    if not file_paths:
        print("[-] Hata: Dosya belirtilmedi!")
        sys.exit(1)
    
    upload_files(file_paths, together=together)


if __name__ == '__main__':
    main()
