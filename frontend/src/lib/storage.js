import { supabase } from './supabaseClient'

// Scaffold de Supabase Storage — todavía no está conectado a ninguna
// vista/feature. Antes de usarlo: crear el bucket correspondiente en el
// dashboard de Supabase (Storage -> New bucket) y sus políticas RLS
// (por defecto un bucket nuevo bloquea todo acceso, incluso autenticado).

export async function uploadFile(bucket, path, file) {
  const { data, error } = await supabase.storage.from(bucket).upload(path, file)

  if (error) throw error

  return data
}

export function getPublicUrl(bucket, path) {
  const { data } = supabase.storage.from(bucket).getPublicUrl(path)

  return data.publicUrl
}
