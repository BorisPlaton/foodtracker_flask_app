create table log_date (
    log_id integer primary key autoincrement,
    entry_date date not null
);

create table food (
    food_id integer primary key autoincrement,
    name text not null,
    fat integer not null,
    protein integer not null,
    carbohydates integer not null,
    calories integer not null
);

create table food_date (
    food_id integer not null,
    log_id integer not null,
    primary key(food_id, log_id)
);