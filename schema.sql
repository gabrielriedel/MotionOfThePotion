create table
  public.global_inventory (
    id integer generated by default as identity,
    created_at timestamp with time zone not null default now(),
    num_green_potions integer null,
    num_green_ml integer null,
    gold integer null,
    num_red_potions integer null,
    num_red_ml integer null,
    num_blue_potions integer null,
    num_blue_ml integer null,
    num_dark_ml integer null,
    num_dark_potions integer null,
    constraint global_inventorty_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.potions (
    id integer generated by default as identity,
    created_at timestamp with time zone not null default now(),
    sku text null,
    name text null,
    price integer null,
    inventory integer null,
    type integer[] null,
    constraint potions_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.carts (
    id integer generated by default as identity,
    customer_name text null,
    character_class text null,
    level integer null,
    constraint carts_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.cart_items (
    id integer generated by default as identity,
    created_at timestamp with time zone not null default now(),
    cart_id integer null,
    potion_sku integer null,
    quantity integer null,
    constraint cart_items_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.barrel_orders (
    id bigint not null,
    created_at timestamp with time zone not null default now(),
    description text null,
    constraint barrel_orders_pkey1 primary key (id)
  ) tablespace pg_default;

  create table
  public.barrel_order_items (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    sku text null,
    ml_per_barrel integer null,
    potion_type integer[] null,
    price integer null,
    quantity integer null,
    order_id integer null,
    constraint barrel_orders_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.gold_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    change integer null,
    description text null,
    constraint gold_ledger_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.ml_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    potion_type integer[] null,
    change integer null,
    description text null,
    constraint ml_ledger_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.potion_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    potion_type integer[] null,
    change integer null,
    description text null,
    constraint potion_ledger_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.capacity (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    ml_cap integer null,
    potion_cap integer null,
    constraint capacity_pkey primary key (id)
  ) tablespace pg_default;

create view
  public.search_view as
select
  cart_items.created_at,
  carts.customer_name,
  cart_items.potion_sku,
  cart_items.quantity,
  cart_items.cost,
  cart_items.id as cart_item_id
from
  cart_items
  join carts on cart_items.cart_id = carts.id;