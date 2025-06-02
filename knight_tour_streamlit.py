import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pyrebase
import json

# Firebase 설정 파일 로드

firebase_config = {
    "apiKey": "AIzaSyABmLjn6d42ihIgWKzvOR-A7nk6tCUbsM0",
    "authDomain": "knight-tour-c4918.firebaseapp.com",
    "projectId": "knight-tour-c4918",
    "storageBucket": "knight-tour-c4918.firebasestorage.app",
    "messagingSenderId": "928407588877",
    "appId": "1:928407588877:web:18a14f58f64da6bf340544"
}

# Firebase 초기화
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# Streamlit UI
st.set_page_config(page_title="나이트 투어", layout="centered")
st.title("🧞‍♂️ 나이트 투어 (Knight's Tour)")

# 사용자 입력
username = st.text_input("회원 이름을 입력해주세요:", max_chars=20)

if username:
    # DB한테에서 사용자 검색하고 없으면 초기화
    user_data = db.child("users").child(username).get().val()
    if user_data is None:
        user_data = {
            "path": [[0, 0]],
            "visited": [[0, 0]],
            "current_pos": [0, 0]
        }
        db.child("users").child(username).set(user_data)

    # 상태를 복사해서 보자
    path = user_data["path"]
    visited = set(tuple(p) for p in user_data["visited"])
    current_pos = tuple(user_data["current_pos"])

    BOARD_SIZE = 5
    KNIGHT_MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                    (-2, -1), (-1, -2), (1, -2), (2, -1)]

    def compute_possible_moves(pos, visited):
        moves = []
        x, y = pos
        for dx, dy in KNIGHT_MOVES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and (nx, ny) not in visited:
                moves.append((nx, ny))
        return moves

    def simulate_possible_moves(pos, visited):
        new_visited = visited | {pos}
        return compute_possible_moves(pos, new_visited)

    def draw_board(show_counts=False):
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_xlim(0, BOARD_SIZE)
        ax.set_ylim(0, BOARD_SIZE)
        ax.set_xticks(np.arange(0, BOARD_SIZE+1))
        ax.set_yticks(np.arange(0, BOARD_SIZE+1))
        ax.grid(True)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                color = 'white' if (i + j) % 2 == 0 else 'lightgray'
                rect = plt.Rectangle((j, BOARD_SIZE-1-i), 1, 1, facecolor=color)
                ax.add_patch(rect)
                if [i, j] in path:
                    move_num = path.index([i, j]) + 1
                    ax.text(j + 0.5, BOARD_SIZE-1-i + 0.5, str(move_num),
                            ha='center', va='center', fontsize=12, color='red')

        i, j = current_pos
        ax.add_patch(plt.Circle((j + 0.5, BOARD_SIZE-1-i + 0.5), 0.3, color='yellow'))

        for move in compute_possible_moves(current_pos, visited):
            mi, mj = move
            rect = plt.Rectangle((mj, BOARD_SIZE-1-mi), 1, 1, fill=False, edgecolor='blue', linewidth=2)
            ax.add_patch(rect)
            if show_counts:
                count = len(simulate_possible_moves(move, visited))
                ax.text(mj + 0.5, BOARD_SIZE-1-mi + 0.5, str(count),
                        ha='center', va='center', fontsize=10, color='blue')

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        st.pyplot(fig)

    st.markdown(f"**현재 위치:** `{current_pos}`")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("되돌리기"):
            if len(path) > 1:
                last = path.pop()
                visited.remove(tuple(last))
                current_pos = tuple(path[-1])
                db.child("users").child(username).update({
                    "path": path,
                    "visited": list(visited),
                    "current_pos": list(current_pos)
                })
    with col2:
        show_counts = st.checkbox("다음 건조 개수 표시", value=False)

    possible = compute_possible_moves(current_pos, visited)
    selected = st.selectbox("이동할 위치 선택", possible if possible else ["이동 불가"])
    if isinstance(selected, tuple) and st.button("이동"):
        path.append(list(selected))
        visited.add(selected)
        current_pos = selected
        db.child("users").child(username).update({
            "path": path,
            "visited": list(visited),
            "current_pos": list(current_pos)
        })
        if len(visited) == BOARD_SIZE * BOARD_SIZE:
            st.success("🎉 모든 칸을 방문했습니다!")

    draw_board(show_counts=show_counts)
