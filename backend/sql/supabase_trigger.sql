-- Script de referencia: correr manualmente en el SQL Editor de Supabase
-- DESPUÉS de que la tabla public.usuarios exista (ej. después de correr
-- `python -m app.init_db` una vez apuntando a la base de Supabase).
--
-- 1) Agrega la FK real de public.usuarios.id -> auth.users.id. No está
--    declarada en el modelo de SQLAlchemy (app/models/usuario.py) porque
--    auth.users vive en un esquema que Supabase gestiona, fuera del
--    Base.metadata que usa create_all() — por eso se agrega acá, por SQL
--    directo, una sola vez.
alter table public.usuarios
  add constraint usuarios_id_fkey
  foreign key (id) references auth.users (id)
  on delete cascade;

-- 2) Crea un trigger que espeja cada alta en auth.users hacia
--    public.usuarios, para que cualquier usuario creado (desde el
--    dashboard, la API admin, un futuro flujo de invitación, etc.) tenga
--    automáticamente su fila de perfil de negocio (nombre, rol, activo).

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.usuarios (id, nombre, email, rol, activo)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'nombre', new.email),
    new.email,
    'empleado',
    true
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Para promover al primer usuario a admin, correr una sola vez:
-- update public.usuarios set rol = 'admin' where email = '<email-del-admin>';
