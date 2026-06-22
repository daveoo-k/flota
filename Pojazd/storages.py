"""Storage z deduplikacją plików po treści.

Wgranie tego samego pliku po raz kolejny nie tworzy duplikatu — nazwa pliku
wynika ze skrótu SHA-256 jego zawartości, więc identyczna treść trafia zawsze
pod tę samą ścieżkę i jest współdzielona. Przydatne w demie pokazywanym
wielokrotnie z tymi samymi zdjęciami.
"""

import hashlib
import os

from django.core.files.storage import FileSystemStorage


class ContentAddressedMixin:
    hash_folder = 'uploads'

    def _content_hash_name(self, name, content):
        # policz skrot tresci (czytamy strumieniowo, potem cofamy wskaznik)
        content.seek(0)
        hasher = hashlib.sha256()
        for chunk in content.chunks():
            hasher.update(chunk)
        content.seek(0)
        digest = hasher.hexdigest()
        ext = os.path.splitext(name or '')[1].lower()
        # rozbicie na podkatalogi po 2 znakach, by nie trzymac wszystkiego w jednym folderze
        return '{folder}/{a}/{b}/{digest}{ext}'.format(
            folder=self.hash_folder, a=digest[:2], b=digest[2:4],
            digest=digest, ext=ext,
        )

    def get_available_name(self, name, max_length=None):
        # NIE dodawaj losowego sufiksu (domyslne zachowanie Django) -
        # chcemy wspoldzielic te sama nazwe dla tej samej tresci
        return name

    def save(self, name, content, max_length=None):
        if name is None:
            name = getattr(content, 'name', 'plik')
        hashed = self._content_hash_name(name, content)
        try:
            if self.exists(hashed):
                # plik o identycznej tresci juz istnieje -> uzyj istniejacego
                return hashed
        except Exception:
            # gdy sprawdzenie sie nie powiedzie, zapis ponizej i tak nadpisze ten sam klucz
            pass
        return super().save(hashed, content, max_length=max_length)


class DedupFileSystemStorage(ContentAddressedMixin, FileSystemStorage):
    """Lokalny development (katalog media/)."""
    pass


# Cloudinary importujemy dopiero, gdy sa dane dostepowe (CLOUDINARY_URL) —
# inaczej sam import biblioteki rzuca bledem (np. lokalnie bez kredencjalow).
try:
    from cloudinary_storage.storage import MediaCloudinaryStorage

    class DedupCloudinaryStorage(ContentAddressedMixin, MediaCloudinaryStorage):
        """Produkcja (Cloudinary)."""
        pass
except Exception:  # brak/niepoprawne kredencjaly Cloudinary
    DedupCloudinaryStorage = None
