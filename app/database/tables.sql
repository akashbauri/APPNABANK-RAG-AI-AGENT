-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. USERS TABLE
create table public.users (
    user_id text primary key, -- Google Subject ID
    name text not null,
    email text unique not null,
    language_preference text default 'en',
    query_count integer default 0,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. QUESTION BANK TABLE
create table public.question_bank (
    id uuid default gen_random_uuid() primary key,
    category text not null, -- 'banking', 'government_schemes', 'stock_market'
    question text not null,
    language text not null default 'en',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. CHAT HISTORY TABLE
create table public.chat_history (
    id uuid default gen_random_uuid() primary key,
    user_id text references public.users(user_id) on delete cascade,
    question text not null,
    answer text not null,
    source_type text not null, -- 'pdf', 'tavily', 'fallback'
    source_name text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. QUERY USAGE LOGS
create table public.query_usage (
    id uuid default gen_random_uuid() primary key,
    user_id text references public.users(user_id) on delete cascade,
    action_type text not null, -- 'text_chat', 'voice_chat'
    tokens_used integer default 0,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 5. FUTURE PAYMENTS TABLE (Staging Setup)
create table public.future_payments (
    id uuid default gen_random_uuid() primary key,
    user_id text references public.users(user_id),
    amount numeric(10, 2) not null,
    currency text default 'INR',
    status text not null, -- 'pending', 'completed', 'failed'
    razorpay_order_id text,
    razorpay_payment_id text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert Default Seed Data into Question Bank
insert into public.question_bank (category, question, language) values
('banking', 'What is FD?', 'en'),
('banking', 'What is RD?', 'en'),
('banking', 'What is UPI?', 'en'),
('banking', 'फिक्स्ड डिपॉजिट (FD) क्या होता है?', 'hi'),
('banking', 'यूपीआई (UPI) क्या है?', 'hi'),
('government_schemes', 'What is PMJDY?', 'en'),
('government_schemes', 'What is PM Mudra Loan?', 'en'),
('government_schemes', 'What is APY?', 'en'),
('government_schemes', 'पीएम किसान योजना क्या है?', 'hi'),
('stock_market', 'What is SIP?', 'en'),
('stock_market', 'What is IPO?', 'en'),
('stock_market', 'What is NIFTY?', 'en'),
('stock_market', 'एसआईपी (SIP) क्या होता है?', 'hi');
