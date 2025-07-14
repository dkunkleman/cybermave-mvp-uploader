import dropbox
import os

DROPBOX_ACCESS_TOKEN = "sl.u.AF2wiTQ6zJpLIhkrY0AMAFIcqC_c8ttFr47AN7siISwx67VL95A_LDQ8xnh4DgFCKg2dm1DLY3bZwnbaqhLTFH2trFYmPFQxY4SrEVHJVXcOgarKrijbbMeN13w9Q5NdhhCAXF7rOTRBI8k3cJn-TcmHG8VQCed8DIpNpV3_nTeoBIzc9ZOGcHVvZMwdIPZQrXxUnRnBiK5xidHobj6aV44w1791keCB9pAnzOAKqvn5NUAC1WpWz5Tdt1fw5KxyEXpBMG1NJKxajTiN7AT6bWPAPQ_Warcq-VmS4TQUL1gKvO1kxlds2Jf8ztRbKHCBOjcz8-rWzKFh0El9Z8thkLetQnurE6_YMLzpH6i8Pq2xk9s8vHCTaYxwqalpWzoe07kB9Dyg8xx4Un8iAmqycUkqZ5wRYI_KD60XwWijJ1t2dlfKoxW4gKYta4adLNN8lypqWMxoxR03NkpQksSbpnn3TbWJzPqWBotkIZMY_QZ7MyJtYN_gKQQBARCQH8cvoouNleZcwWjuVSqMgg-UvQNQ0kcOEoK9Ip2xX-AWky4ygiJjz9yKFh5wVYFI_HA6rCvqlaPZPztb63dxW8fJHgWIhDYzrk0ZkrnXlEkXfB9-4KwmQaeFtFpwTtx2xDLcZi5p-uA2HBRNVsdtB37ik5IzUgWfZ47ZCKljM9p1aS8CReQWbKltg7cZL7fq4Akmc2Y38MIBR1im4xWOLhkeY1VMR_97CpPGr_kfKa5Z88J8N0qu-_cWttqnFFCe6apNWDVlTU-0fPmberWsQok0pmILIOOF8A1q0ciXYxZQ8qTYZF_DfUQ2xN1vXFQUR610q6LFOsiuD4WTJ4VgXCw1N3_ZpgVoF-0xxpJO2Q0QByfhUwsWwsjVvuYn2UWU6AWcwiMgM8ydrdcpMvYS8VkKBdBXKdRjKphYPI1r4V_w_mtF7GYFjBDOwnvbHb3GvUVvkBiNa5em0JAKF_u0N7LwDmKBvBj-uHbm5LTkROHePTZx1dhGBRxfts6mU73sFCGAgbOL18a6c6qdXBH52fnTSxmjYwS8aX3QSIEBVo-2y3DvREsp8h9XjIGx2YUKjpV9msFor9tw5S1Nc9ElB9Ke0GMCERyx7ZeB0vgsdGFIhxy4Ue4w8rLTHBn_JUBTkRoHoGM54YL-ILLrqwamrMK-AAPN5U-l3PeWrRe-YwQxV2W5LCb2HAOuZ2kMHvi0oV--sP0MdpGGi6TScebA5VZFEpByMSIxlUssWPMBG2Qg3R7WbyHS-iyP9t5PIVQMBn6qME-YoZWXOHFXiM0P0Pq6lJ56"
SOURCE_FOLDER = "/Full Court Docket Files"
DEST_FOLDER = "vault/memory/"

dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def download_all_files():
    os.makedirs(DEST_FOLDER, exist_ok=True)

    try:
        entries = dbx.files_list_folder(SOURCE_FOLDER).entries
    except Exception as e:
        print(f"Failed to list folder: {e}")
        return

    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            filename = entry.name
            dest_path = os.path.join(DEST_FOLDER, filename)

            try:
                metadata, res = dbx.files_download(entry.path_display)
                with open(dest_path, "wb") as f:
                    f.write(res.content)
                print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    download_all_files()
